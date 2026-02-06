# AxnosAI

AxnosAI is an AI-powered data exploration chatbot that allows users to interact with datasets using natural language. It enables seamless analysis of structured and semi-structured data such as CSV, Excel, JSON, and PDF files by translating user queries into intelligent data operations.

---

## 🚀 Features

- Natural language chatbot for data analysis  
- Supports CSV, Excel, JSON, and PDF file formats  
- Converts user questions into Pandas-based data operations  
- Fast and interactive data insights  
- Modular microservices architecture  
- Secure authentication and request orchestration  
- Clean and responsive user interface  

---

## 📁 Project Structure


Frontend
```
├── 📁 app
│   ├── 📁 auth
│   │   └── 📄 page.tsx
│   ├── 📁 dashboard
│   │   └── 📄 page.tsx
│   ├── 📄 favicon.ico
│   ├── 🎨 globals.css
│   ├── 📄 layout.tsx
│   └── 📄 page.tsx
├── 📁 components
│   └── 📄 AuthPage.tsx
├── 📁 context
│   └── 📄 AuthContext.tsx
├── 📁 lib
│   └── 📄 api.ts
├── 📁 middleware
│   └── 📄 middleware.ts
├── 📁 public
│   ├── 🖼️ file.svg
│   ├── 🖼️ globe.svg
│   ├── 🖼️ next.svg
│   ├── 🖼️ vercel.svg
│   └── 🖼️ window.svg
├── ⚙️ .gitignore
├── 📝 README.md
├── 📄 eslint.config.mjs
├── 📄 next.config.ts
├── ⚙️ package-lock.json
├── ⚙️ package.json
├── 📄 postcss.config.mjs
└── ⚙️ tsconfig.json
```

Backend
```
├── 📁 AXNOSAI
│   ├── 🖼️ 1.png
│   └── 🖼️ 2.png
├── 📁 auth-service
│   ├── 📁 src
│   │   ├── 📁 controllers
│   │   │   └── 📄 auth.controller.ts
│   │   ├── 📁 dto
│   │   │   ├── 📄 login.dto.ts
│   │   │   └── 📄 register.dto.ts
│   │   ├── 📁 schemas
│   │   │   └── 📄 user.schema.ts
│   │   ├── 📁 services
│   │   │   └── 📄 auth.service.ts
│   │   ├── 📄 app.controller.spec.ts
│   │   ├── 📄 app.controller.ts
│   │   ├── 📄 app.module.ts
│   │   ├── 📄 app.service.ts
│   │   └── 📄 main.ts
│   ├── 📁 test
│   │   ├── 📄 app.e2e-spec.ts
│   │   └── ⚙️ jest-e2e.json
│   ├── ⚙️ .gitignore
│   ├── ⚙️ .prettierrc
│   ├── 📝 README.md
│   ├── 📄 eslint.config.mjs
│   ├── ⚙️ nest-cli.json
│   ├── ⚙️ package-lock.json
│   ├── ⚙️ package.json
│   └── ⚙️ tsconfig.json
├── 📁 main-backend-service
│   ├── 📁 chat_config
│   │   ├── 📁 migrations
│   │   │   ├── 🐍 0001_initial.py
│   │   │   ├── 🐍 0002_chat_name_generated.py
│   │   │   ├── 🐍 0003_chat_source_type.py
│   │   │   ├── 🐍 0004_alter_chat_dataset.py
│   │   │   └── 🐍 __init__.py
│   │   ├── 📁 utils
│   │   │   └── 🐍 auto_generate_chat_name.py
│   │   ├── 🐍 __init__.py
│   │   ├── 🐍 admin.py
│   │   ├── 🐍 apps.py
│   │   ├── 🐍 models.py
│   │   ├── 🐍 serializers.py
│   │   ├── 🐍 tests.py
│   │   ├── 🐍 urls.py
│   │   └── 🐍 views.py
│   ├── 📁 code_execution
│   │   ├── 📁 migrations
│   │   │   └── 🐍 __init__.py
│   │   ├── 🐍 __init__.py
│   │   ├── 🐍 admin.py
│   │   ├── 🐍 apps.py
│   │   ├── 🐍 models.py
│   │   ├── 🐍 tests.py
│   │   └── 🐍 views.py
│   ├── 📁 code_generation
│   │   ├── 📁 migrations
│   │   │   └── 🐍 __init__.py
│   │   ├── 📁 utils
│   │   │   └── 🐍 code_generation_service.py
│   │   ├── 🐍 __init__.py
│   │   ├── 🐍 admin.py
│   │   ├── 🐍 apps.py
│   │   ├── 🐍 models.py
│   │   ├── 🐍 tests.py
│   │   ├── 🐍 urls.py
│   │   └── 🐍 views.py
│   ├── 📁 core
│   │   ├── 🐍 __init__.py
│   │   ├── 🐍 asgi.py
│   │   ├── 🐍 settings.py
│   │   ├── 🐍 urls.py
│   │   └── 🐍 wsgi.py
│   ├── 📁 data_config
│   │   ├── 📁 migrations
│   │   │   ├── 🐍 0001_initial.py
│   │   │   └── 🐍 __init__.py
│   │   ├── 📁 utils
│   │   │   └── 🐍 supabase_client.py
│   │   ├── 🐍 __init__.py
│   │   ├── 🐍 admin.py
│   │   ├── 🐍 apps.py
│   │   ├── 🐍 models.py
│   │   ├── 🐍 serializers.py
│   │   ├── 🐍 tests.py
│   │   ├── 🐍 urls.py
│   │   └── 🐍 views.py
│   ├── 📁 db_connection
│   │   ├── 📁 migrations
│   │   │   └── 🐍 __init__.py
│   │   ├── 📁 utils
│   │   │   └── 🐍 pool.py
│   │   ├── 🐍 __init__.py
│   │   ├── 🐍 admin.py
│   │   ├── 🐍 apps.py
│   │   ├── 🐍 models.py
│   │   ├── 🐍 tests.py
│   │   ├── 🐍 urls.py
│   │   └── 🐍 views.py
│   ├── 📁 main-venv
│   │   ├── 📁 Scripts
│   │   │   ├── 📄 Activate.ps1
│   │   │   ├── 📄 activate
│   │   │   ├── 📄 activate.bat
│   │   │   ├── ⚙️ build_sync.exe
│   │   │   ├── 📄 deactivate.bat
│   │   │   ├── ⚙️ django-admin.exe
│   │   │   ├── ⚙️ dotenv.exe
│   │   │   ├── ⚙️ f2py.exe
│   │   │   ├── ⚙️ httpx.exe
│   │   │   ├── ⚙️ nltk.exe
│   │   │   ├── ⚙️ normalizer.exe
│   │   │   ├── ⚙️ numpy-config.exe
│   │   │   ├── ⚙️ pip.exe
│   │   │   ├── ⚙️ pip3.10.exe
│   │   │   ├── ⚙️ pip3.exe
│   │   │   ├── ⚙️ python.exe
│   │   │   ├── ⚙️ pythonw.exe
│   │   │   ├── ⚙️ sqlformat.exe
│   │   │   ├── ⚙️ tests.exe
│   │   │   ├── ⚙️ tqdm.exe
│   │   │   └── ⚙️ websockets.exe
│   │   └── 📄 pyvenv.cfg
│   ├── 📁 user_input
│   │   ├── 📁 migrations
│   │   │   └── 🐍 __init__.py
│   │   ├── 🐍 __init__.py
│   │   ├── 🐍 admin.py
│   │   ├── 🐍 apps.py
│   │   ├── 🐍 models.py
│   │   ├── 🐍 tests.py
│   │   └── 🐍 views.py
│   └── 🐍 manage.py
├── 📁 proxy-orchestration-server
│   ├── 📁 env-proxy
│   │   └── 📄 pyvenv.cfg
│   ├── 📝 README.md
│   ├── 🐍 main.py
│   └── 📄 requirements.txt
├── ⚙️ .gitignore
├── 📕 Axnos_Synopsis_Final_End.pdf
├── 📝 README.md
└── 📄 api.http
```



