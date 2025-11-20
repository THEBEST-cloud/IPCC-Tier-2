"""
Main FastAPI application for Reservoir Emissions Tool
"""

from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import jwt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

from . import models, schemas, auth
from .database import engine, get_db
from .ipcc_tier1 import (
    get_climate_region,
    assess_trophic_status,
    calculate_emissions,
    calculate_ipcc_tier1_emissions,
    clean_numeric_value
)
from .climate_zones import get_climate_zone_details, map_standard_to_aggregated_cn
from .analysis import run_full_analysis

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize default users
def init_default_users():
    """Initialize default users for testing"""
    db = next(get_db())
    try:
        # Check if demo user already exists
        existing_user = auth.get_user_by_username(db, "demo")
        if not existing_user:
            # Create demo user
            demo_user = models.User(
                username="demo",
                email="demo@example.com",
                hashed_password=auth.get_password_hash("demo123"),
                first_name="Demo",
                last_name="User",
                organization="Demo Organization",
                is_active=True,
                is_verified=True
            )
            db.add(demo_user)
            db.commit()
            print("Demo user created successfully: demo/demo123")
        else:
            print("Demo user already exists")
    except Exception as e:
        print(f"Error creating demo user: {e}")
        db.rollback()
    finally:
        db.close()

# Initialize default users on startup
init_default_users()

# JWT Configuration (moved to auth.py)

# Initialize FastAPI app
app = FastAPI(
    title="Reservoir Carbon Accounting",
    description="水库碳核算系统 - IPCC Tier 1 Methodology for Reservoir Greenhouse Gas Emissions",
    version="1.0.0"
)

# Security
security = HTTPBearer()

# Email configuration
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", EMAIL_USER)

def send_password_reset_email(email: str, token: str, request: Request):
    """Send password reset email"""
    try:
        # 构建重置链接
        reset_url = f"{request.url.scheme}://{request.url.netloc}/reset-password?token={token}"
        
        # 创建邮件内容
        subject = "水库碳核算系统 - 密码重置"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f9f9f9; }}
                .button {{ display: inline-block; padding: 12px 24px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>密码重置请求</h1>
                </div>
                <div class="content">
                    <p>您好，</p>
                    <p>我们收到了您的密码重置请求。请点击下面的按钮来重置您的密码：</p>
                    <a href="{reset_url}" class="button">重置密码</a>
                    <p>如果按钮无法点击，请复制以下链接到浏览器地址栏：</p>
                    <p style="word-break: break-all; background: #eee; padding: 10px;">{reset_url}</p>
                    <p><strong>注意：</strong>此链接将在1小时后过期。</p>
                    <p>如果您没有请求密码重置，请忽略此邮件。</p>
                </div>
                <div class="footer">
                    <p>水库碳核算系统 | Reservoir Carbon Accounting</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # 如果配置了邮件服务，发送邮件
        if EMAIL_USER and EMAIL_PASSWORD:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = EMAIL_FROM
            msg['To'] = email
            
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)
            server.quit()
            
            return True
        else:
            # 如果没有配置邮件服务，在控制台输出重置链接（开发环境）
            print(f"=== 密码重置链接 ===")
            print(f"邮箱: {email}")
            print(f"重置链接: {reset_url}")
            print(f"令牌: {token}")
            print(f"==================")
            return True
            
    except Exception as e:
        print(f"邮件发送失败: {e}")
        return False

# JWT Token verification function
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    username = auth.verify_token(credentials.credentials)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return username

# Setup templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Serve static files
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Redirect to login page"""
    return RedirectResponse(url="/login")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Serve the main web interface"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/analyze", response_model=schemas.AnalysisResponse)
async def analyze_reservoir(
    reservoir_input: schemas.ReservoirInput,
    db: Session = Depends(get_db)
):
    """
    Analyze reservoir emissions using IPCC Tier 1 methodology
    """
    # Determine climate region
    # 支持两种覆盖值：
    # 1) 中文聚合气候区（前端下拉现在传中文）
    # 2) 英文标准气候区（兼容旧前端）
    if reservoir_input.climate_region_override:
        # 如果传来的是中文六大聚合气候区，直接使用
        cn_override = reservoir_input.climate_region_override
        available_cn = {"北方", "冷温带", "暖温带干旱", "暖温带湿润", "热带干旱/山地", "热带湿润/潮湿"}
        if cn_override in available_cn:
            climate_region = cn_override
        else:
            # 否则尝试把英文标准映射为中文聚合
            mapped_cn = map_standard_to_aggregated_cn(reservoir_input.climate_region_override)
            climate_region = mapped_cn or get_climate_region(reservoir_input.latitude, reservoir_input.longitude)
    else:
        climate_region = get_climate_region(reservoir_input.latitude, reservoir_input.longitude)
    
    # Assess trophic status
    trophic_status = None
    if reservoir_input.trophic_status:
        # 用户直接选择了营养状态
        trophic_status = reservoir_input.trophic_status
    elif reservoir_input.water_quality:
        # 通过水质参数自动评估
        wq = reservoir_input.water_quality
        trophic_status = assess_trophic_status(
            total_phosphorus=wq.total_phosphorus,
            total_nitrogen=wq.total_nitrogen,
            chlorophyll_a=wq.chlorophyll_a,
            secchi_depth=wq.secchi_depth
        )
    
    # 使用IPCC Tier 1方法计算排放
    # 转换面积单位：km² -> ha
    surface_area_ha = reservoir_input.surface_area * 100
    
    # 执行IPCC Tier 1计算
    ipcc_results = calculate_ipcc_tier1_emissions(
        surface_area_ha=surface_area_ha,
        latitude=reservoir_input.latitude,
        longitude=reservoir_input.longitude,
        trophic_status=trophic_status,
        reservoir_age=reservoir_input.reservoir_age,
        climate_region_override=climate_region
    )
    
    # 提取主要结果
    ch4_total = clean_numeric_value(ipcc_results["E_CH4_total"])  # tCO2eq
    co2_total = clean_numeric_value(ipcc_results["E_CO2_total"])  # tCO2eq
    n2o_total = 0  # IPCC Tier 1中N2O忽略
    co2_eq = clean_numeric_value(ipcc_results["E_total"])  # tCO2eq
    print(f"co2_eq: {co2_eq}")

    
    # Run uncertainty and sensitivity analysis
    uncertainty_results, sensitivity_results = run_full_analysis(
        surface_area_ha=surface_area_ha,  # 使用公顷为单位
        latitude=reservoir_input.latitude,
        longitude=reservoir_input.longitude,
        trophic_status=trophic_status,
        reservoir_age=reservoir_input.reservoir_age or 100,  # 默认100年
        climate_region_override=climate_region,
        run_uncertainty=reservoir_input.run_uncertainty,
        run_sensitivity=reservoir_input.run_sensitivity,
        iterations=reservoir_input.uncertainty_iterations
    )
    
    # Store in database
    db_analysis = models.ReservoirAnalysis(
        latitude=reservoir_input.latitude,
        longitude=reservoir_input.longitude,
        climate_region=climate_region,
        total_phosphorus=reservoir_input.water_quality.total_phosphorus if reservoir_input.water_quality else None,
        total_nitrogen=reservoir_input.water_quality.total_nitrogen if reservoir_input.water_quality else None,
        chlorophyll_a=reservoir_input.water_quality.chlorophyll_a if reservoir_input.water_quality else None,
        secchi_depth=reservoir_input.water_quality.secchi_depth if reservoir_input.water_quality else None,
        trophic_status=trophic_status,
        surface_area=reservoir_input.surface_area,
        reservoir_age=reservoir_input.reservoir_age,
        ch4_emission_factor=clean_numeric_value(ipcc_results["EF_CH4_age_le_20"]),
        co2_emission_factor=clean_numeric_value(ipcc_results["EF_CO2_age_le_20"]),
        total_ch4_emissions=ch4_total,
        total_co2_emissions=co2_total,
        co2_equivalent=co2_eq,
        uncertainty_analysis=uncertainty_results,
        sensitivity_analysis=sensitivity_results,
        user_inputs=reservoir_input.dict()
    )
    
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)
    
    # Prepare response with detailed IPCC Tier 1 results
    emission_results = schemas.EmissionResults(
        total_ch4_emissions=ch4_total,
        total_co2_emissions=co2_total,
        total_n2o_emissions=n2o_total,
        co2_equivalent=co2_eq,
        ch4_emission_factor=clean_numeric_value(ipcc_results["EF_CH4_age_le_20"]),
        co2_emission_factor=clean_numeric_value(ipcc_results["EF_CO2_age_le_20"]),
        n2o_emission_factor=0.0,  # IPCC Tier 1中N2O忽略
        climate_region=ipcc_results["climate_region"],
        trophic_status=trophic_status,
        # 添加IPCC Tier 1详细结果
        ipcc_tier1_results=ipcc_results
    )
    
    return schemas.AnalysisResponse(
        id=db_analysis.id,
        created_at=db_analysis.created_at,
        latitude=reservoir_input.latitude,
        longitude=reservoir_input.longitude,
        surface_area=reservoir_input.surface_area,
        climate_region=climate_region,
        trophic_status=trophic_status,
        emissions=emission_results,
        uncertainty=uncertainty_results,
        sensitivity=sensitivity_results
    )


@app.get("/api/analyses", response_model=List[schemas.AnalysisListItem])
async def list_analyses(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get list of all analyses
    """
    analyses = db.query(models.ReservoirAnalysis).order_by(
        models.ReservoirAnalysis.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return analyses


@app.get("/api/analyses/{analysis_id}", response_model=schemas.AnalysisResponse)
async def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    """
    Get specific analysis by ID
    """
    analysis = db.query(models.ReservoirAnalysis).filter(
        models.ReservoirAnalysis.id == analysis_id
    ).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    emission_results = schemas.EmissionResults(
        total_ch4_emissions=analysis.total_ch4_emissions,
        total_co2_emissions=analysis.total_co2_emissions,
        total_n2o_emissions=analysis.total_n2o_emissions,
        co2_equivalent=analysis.co2_equivalent,
        ch4_emission_factor=analysis.ch4_emission_factor,
        co2_emission_factor=analysis.co2_emission_factor,
        n2o_emission_factor=analysis.n2o_emission_factor,
        climate_region=analysis.climate_region,
        trophic_status=analysis.trophic_status
    )
    
    return schemas.AnalysisResponse(
        id=analysis.id,
        created_at=analysis.created_at,
        latitude=analysis.latitude,
        longitude=analysis.longitude,
        surface_area=analysis.surface_area,
        climate_region=analysis.climate_region,
        trophic_status=analysis.trophic_status,
        emissions=emission_results,
        uncertainty=analysis.uncertainty_analysis,
        sensitivity=analysis.sensitivity_analysis
    )


@app.delete("/api/analyses/{analysis_id}")
async def delete_analysis(analysis_id: int, db: Session = Depends(get_db)):
    """
    Delete specific analysis
    """
    analysis = db.query(models.ReservoirAnalysis).filter(
        models.ReservoirAnalysis.id == analysis_id
    ).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    db.delete(analysis)
    db.commit()
    
    return {"message": "Analysis deleted successfully"}


@app.get("/api/climate-region/{latitude}/{longitude}")
async def get_climate_info(latitude: float, longitude: float):
    """
    根据经纬度返回气候带信息：
    - raw_standard_en: 映射前的IPCC标准气候区（英文）
    - aggregated_en: 映射后的IPCC聚合气候区（英文）
    - aggregated_cn: 映射后的IPCC聚合气候区（中文）
    - koppen_code: 原始柯本代码（字符串）

    前端仅显示 raw_standard_en；后端计算继续使用 aggregated_cn。
    """
    details = get_climate_zone_details(latitude, longitude)
    if details is None:
        # 回退到旧逻辑，确保接口稳定
        fallback = get_climate_region(latitude, longitude)
        return {
            "latitude": latitude,
            "longitude": longitude,
            "climate_region": fallback,
            "raw_standard_en": None,
            "aggregated_en": None,
            "aggregated_cn": fallback,
            "koppen_code": None,
        }

    return {
        "latitude": latitude,
        "longitude": longitude,
        "climate_region": details.get("aggregated_zone_cn"),
        "raw_standard_en": details.get("standard_zone_en"),
        "aggregated_en": details.get("aggregated_zone_en"),
        "aggregated_cn": details.get("aggregated_zone_cn"),
        "koppen_code": details.get("koppen_code"),
        "koppen_code_str": details.get("koppen_code_str"),
        "koppen_cn_name": details.get("koppen_cn_name"),
    }


# User Authentication Routes
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Serve login page"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Serve register page"""
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    """Serve profile page"""
    raise HTTPException(status_code=404, detail="Not Found")

@app.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    """Serve forgot password page"""
    return templates.TemplateResponse("forgot-password.html", {"request": request})

@app.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page(request: Request, token: str = None):
    """Serve reset password page"""
    return templates.TemplateResponse("reset-password.html", {"request": request, "token": token})


@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """Serve user settings page"""
    raise HTTPException(status_code=404, detail="Not Found")


@app.get("/methodology", response_class=HTMLResponse)
async def methodology_page(request: Request):
    """Serve methodology page"""
    return templates.TemplateResponse("methodology.html", {"request": request})

@app.get("/help", response_class=HTMLResponse)
async def help_page(request: Request):
    """Serve help page"""
    return templates.TemplateResponse("help.html", {"request": request})

@app.get("/results/{analysis_id}", response_class=HTMLResponse)
async def results_page(request: Request, analysis_id: int):
    """Serve results page"""
    return templates.TemplateResponse("results.html", {
        "request": request, 
        "analysis_id": analysis_id
    })

# User Authentication API
@app.post("/api/auth/login")
async def login(credentials: schemas.LoginRequest, db: Session = Depends(get_db)):
    """User login"""
    user = auth.authenticate_user(db, credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/auth/register")
async def register(user_data: schemas.RegisterRequest, db: Session = Depends(get_db)):
    """User registration"""
    try:
        user = auth.create_user(db, user_data)
        access_token = auth.create_access_token(data={"sub": user.username})
        return {"access_token": access_token, "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@app.post("/api/auth/forgot-password", response_model=schemas.MessageResponse)
async def forgot_password(request_data: schemas.ForgotPasswordRequest, request: Request, db: Session = Depends(get_db)):
    """Request password reset"""
    token = auth.create_password_reset_token(db, request_data.email)
    
    if token:
        # 发送密码重置邮件
        email_sent = send_password_reset_email(request_data.email, token, request)
        
        if email_sent:
            return schemas.MessageResponse(
                success=True,
                message="如果该邮箱地址存在，您将收到密码重置链接"
            )
        else:
            return schemas.MessageResponse(
                success=False,
                message="邮件发送失败，请稍后重试"
            )
    else:
        # 为了安全起见，即使邮箱不存在也返回相同的消息
        return schemas.MessageResponse(
            success=True,
            message="如果该邮箱地址存在，您将收到密码重置链接"
        )

@app.post("/api/auth/reset-password", response_model=schemas.MessageResponse)
async def reset_password(request: schemas.ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset password using token"""
    success = auth.reset_user_password(db, request.token, request.new_password)
    
    if success:
        return schemas.MessageResponse(
            success=True,
            message="密码重置成功，请使用新密码登录"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效或已过期的重置令牌"
        )

@app.get("/api/auth/verify-reset-token/{token}")
async def verify_reset_token(token: str, db: Session = Depends(get_db)):
    """Verify if a reset token is valid"""
    user = auth.verify_password_reset_token(db, token)
    
    if user:
        return {"valid": True, "email": user.email}
    else:
        return {"valid": False}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}
