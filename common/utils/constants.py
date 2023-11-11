# 短信验证码超时时间
SMS_CODE_EXPIRE_SECOND = 60 * 10  # 1分钟

# 短信存入redis中的key
SMS_REDIS_KEY_PREFIX = "app:sms:code:"

# TOKEN过期时间（分钟）
TOKEN_EXPIRE_MIN = 2 * 60  # 2小时

# REFRESH_TOKEN过期时间（分钟）
REFRESH_TOKEN_EXPIRE_MIN = 24 * 60 * 7  # 7天
