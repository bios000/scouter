# Scouter - 子域名收集工具

Scouter 是一个用 Python 编写的子域名收集工具，能够从多个数据源自动收集和验证目标域名的子域名信息。

## 特点

- 多数据源支持：集成多个搜索引擎和在线服务
- 自动化收集：自动处理搜索引擎的反爬机制
- 代理支持：支持配置 HTTP/HTTPS/SOCKS 代理
- 结果验证：自动验证和去重收集到的子域名
- 模块化设计：易于扩展新的数据源

## 已支持的数据源

### 信息&&空间搜索引擎
- Google 搜索  ✅
- 百度搜索 ✅
- Bing 搜索 ✅
- 奇安信鹰图 ✅
- Shodan ✅
- Fofa ✅
- Quake360 ✅
- shodan ✅

### 证书透明度收集子域
- crt.sh ✅
- Certspotter ✅
- Censys CT ✅
- SSLMate CT ✅


### DNS 服务
- 公共 DNS 记录查询
  - A 记录
  - CNAME 记录
  - MX 记录
  - NS 记录
  - TXT 记录

### 代码库搜集
- GitHub 代码仓库搜索 ✅
- gitee 代码仓库搜索(官方api 不可用) ❌




## 安装

```bash
# 克隆仓库
git clone https://github.com/your-username/scouter.git
cd scouter

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

## 配置

首次运行时需要配置各服务的 API 密钥：

```bash
python scouter.py config
```

### 代理配置

支持以下格式的代理配置：
- HTTP 代理：`http://host:port`
- HTTPS 代理：`https://host:port`
- SOCKS 代理：`socks5://host:port`

## 使用方法

基本使用：
```bash
python scouter.py domain example.com
```

指定数据源：
```bash
python scouter.py domain example.com --sources google,bing,dns
```

## 注意事项

1. 搜索引擎查询可能触发验证码，建议：
   - 使用代理
   - 适当调整查询间隔
   - 在遇到验证码时手动处理

2. API 限制：
   - 部分 API 服务需要付费订阅
   - 注意遵守 API 的速率限制
   - 建议在配置文件中设置有效的 API 密钥

3. 代理使用：
   - 建议使用稳定的代理服务
   - 支持多种代理协议
   - 可以配置多个代理进行轮换

## 开发计划

- [ ] 添加更多数据源支持
- [ ] 改进验证码处理机制
- [ ] 添加并发查询支持
- [ ] 优化结果输出格式
- [ ] 添加 Web 界面

## 贡献

欢迎提交 Pull Request 或创建 Issue。

## 许可证

[MIT License](LICENSE)
