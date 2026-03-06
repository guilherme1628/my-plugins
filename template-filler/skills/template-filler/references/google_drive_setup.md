# Google Drive Setup Guide

This document explains how to configure Google Drive for use with Template_Filler.

## Prerequisites

- Google Cloud account
- Access to Google Cloud Console
- Google Drive account

## Step-by-Step Setup

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select an existing one
3. Note the project ID for later use

### 2. Enable Required APIs

Enable the following APIs for your project:

1. **Google Drive API**
   - Go to APIs & Services → Library
   - Search for "Google Drive API"
   - Click Enable

2. **Google Docs API**
   - Go to APIs & Services → Library
   - Search for "Google Docs API"
   - Click Enable

### 3. Create Service Account

1. Go to **IAM & Admin → Service Accounts**
2. Click **Create Service Account**
3. Fill in details:
   - **Name**: `template-filler-sa` (or any name you prefer)
   - **Description**: "Service account for Template_Filler automation"
4. Click **Create and Continue**
5. Skip role assignment (optional)
6. Click **Done**

### 4. Generate Credentials

1. Click on the newly created service account
2. Go to **Keys** tab
3. Click **Add Key → Create new key**
4. Choose **JSON** format
5. Click **Create**
6. Save the downloaded JSON file securely
7. Note the file path - you'll need it for configuration

### 5. Get Service Account Email

From the service account page, copy the email address. It looks like:

```
template-filler-sa@your-project-id.iam.gserviceaccount.com
```

You'll need this email to share folders in Google Drive.

### 6. Create Folder Structure in Google Drive

1. Go to [Google Drive](https://drive.google.com)
2. Create the main folder: `Template_Filler`
3. Inside it, create the following subfolders:

```
Template_Filler/
├── Templates/                  (store your template files here)
├── Documentos_Gerados/        (generated documents go here)
│   └── 2025/                  (organized by year)
│       ├── 01-Janeiro/
│       ├── 02-Fevereiro/
│       └── ...
└── Config/                     (optional - for configuration files)
```

### 7. Share Folders with Service Account

1. Right-click on the `Template_Filler` folder
2. Click **Share**
3. Paste the service account email
4. Set permission to **Editor**
5. Uncheck "Notify people"
6. Click **Share**

The service account now has access to the folder and all subfolders.

### 8. Get Folder ID (Optional)

To get the root folder ID for better performance:

1. Open the `Template_Filler` folder in Google Drive
2. Look at the URL in your browser:
   ```
   https://drive.google.com/drive/folders/1a2b3c4d5e6f7g8h9i0j
   ```
3. The folder ID is the part after `/folders/`: `1a2b3c4d5e6f7g8h9i0j`
4. Save this for environment configuration

## Configuration

### Environment Variables

Create a `.env` file in your project root with:

```bash
# Required: Path to service account credentials JSON
GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/credentials.json"

# Optional: Root folder ID for better performance
TEMPLATE_FILLER_DRIVE_FOLDER_ID="1a2b3c4d5e6f7g8h9i0j"

# Optional: Logging level
TEMPLATE_FILLER_LOG_LEVEL="INFO"
```

### Testing Connection

Test your setup with:

```bash
python3 scripts/list_templates.py
```

If configured correctly, it will list all templates in your Templates/ folder.

## Template Naming Convention

Templates must follow this naming pattern:

```
TEMPLATE_{Type}_{Description}.gdoc
```

**Examples**:
- `TEMPLATE_Contrato_Prestacao_Servicos.gdoc`
- `TEMPLATE_Invoice_Mensal.gdoc`
- `TEMPLATE_Proposta_Comercial.gdoc`
- `TEMPLATE_Termo_Confidencialidade.gdoc`

## Generated Document Organization

Documents are automatically organized by:

1. **Document type** (extracted from template name)
2. **Year** (current year)
3. **Month** (current month)

**Naming pattern**:
```
{TemplateType}_{Client}_{Date}_{Sequential}.gdoc
```

**Examples**:
- `Contrato_ACME_CORP_2025-01-15_001.gdoc`
- `Invoice_ClienteXYZ_2025-02-01_045.gdoc`

## Security Best Practices

### Credentials File

- **Never commit** credentials JSON to version control
- Add to `.gitignore`:
  ```
  credentials.json
  *-credentials.json
  *.json
  .env
  ```

### Service Account Permissions

- Use **minimal permissions** required
- Share only the specific folders needed
- Consider using separate service accounts for different environments (dev/prod)
- Rotate credentials periodically (recommended: every 90 days)

### Access Control

- Limit who can access the service account credentials
- Use environment variables instead of hardcoding paths
- Store credentials securely (use secrets management tools in production)

## Troubleshooting

### "Credentials not found" Error

**Problem**: `GOOGLE_APPLICATION_CREDENTIALS` environment variable not set

**Solution**:
1. Check `.env` file exists and is loaded
2. Verify the path to credentials JSON is absolute, not relative
3. Ensure the file exists and is readable

### "Insufficient Permission" Error

**Problem**: Service account lacks access to Drive folder

**Solution**:
1. Verify folder is shared with service account email
2. Check permission level is "Editor" not just "Viewer"
3. Ensure you didn't check "Notify people" which might block sharing

### "API not enabled" Error

**Problem**: Required Google APIs not enabled

**Solution**:
1. Go to Google Cloud Console
2. Enable Google Drive API
3. Enable Google Docs API
4. Wait a few minutes for changes to propagate

### "Template not found" Error

**Problem**: Templates folder is empty or files don't match naming pattern

**Solution**:
1. Check files are in `Templates/` subfolder
2. Verify filenames start with `TEMPLATE_`
3. Ensure service account has access to the folders
4. Try listing files manually in Google Drive web interface

### Rate Limit Errors

**Problem**: Too many API requests in short time

**Solution**:
1. Reduce request frequency
2. Implement exponential backoff
3. Consider requesting quota increase from Google
4. Default quota: 100 requests/user/100 seconds

## Quota Limits

Google Drive API has the following default quotas:

- **Queries per user per 100 seconds**: 1,000
- **Queries per project per day**: 1,000,000,000

These are usually sufficient for typical Template_Filler usage. Monitor usage in Google Cloud Console if needed.

## Advanced: Multiple Environments

For dev/staging/production environments:

```bash
# Development
GOOGLE_APPLICATION_CREDENTIALS="/path/to/dev-credentials.json"
TEMPLATE_FILLER_DRIVE_FOLDER_ID="dev_folder_id"

# Production
GOOGLE_APPLICATION_CREDENTIALS="/path/to/prod-credentials.json"
TEMPLATE_FILLER_DRIVE_FOLDER_ID="prod_folder_id"
```

Use different service accounts and folder structures for each environment.
