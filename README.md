

#  API Testing Guide (Postman)

##  **1. Image OCR Endpoint**

**URL (POST):**

```
http://localhost:8000/extract-recipe/image
```

### **Headers**

| Key          | Value                 |
| ------------ | --------------------- |
| X-API-Key    | your-secret-api-token |
| Content-Type | application/json      |

### **Body → form-data**

| Key  | Value         | Type |
| ---- | ------------- | ---- |
| file | {select file} | File |

---

##  **2. Article Scraper Endpoint**

**URL (POST):**

```
http://localhost:8000/extract-recipe/article
```

### **Headers**

| Key          | Value                 |
| ------------ | --------------------- |
| X-API-Key    | your-secret-api-token |
| Content-Type | application/json      |

### **Body → raw JSON**

```json
{
    "url": "article-url",
}
```

---

##  **3. Social Media Scraper Endpoint**

**URL (POST):**

```
http://localhost:8000/extract-recipe/social
```

### **Headers**

| Key          | Value                 |
| ------------ | --------------------- |
| X-API-Key    | your-secret-api-token |
| Content-Type | application/json      |

### **Body → raw JSON**

```json
{
    "url": "social-url",
}
```



env setup:

# Groq API Configuration
GROQ_API_KEY=gsk_LjvS6....

# API Security
STATIC_API_TOKEN=your_key

# Rate Limiting (optional)
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600