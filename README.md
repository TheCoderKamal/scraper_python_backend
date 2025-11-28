

#  API Testing Guide (Postman)

##  **1. Image OCR Endpoint**

**URL (POST):**

```
http://localhost:8000/scrape/image
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
http://localhost:8000/scrape/article
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
http://localhost:8000/scrape/social
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

