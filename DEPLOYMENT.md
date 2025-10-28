# Deploying to Vercel

## Steps to Deploy:

### 1. Push to GitHub

First, initialize git and push your code to GitHub:

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Poker game"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/poker-game-ui.git
git branch -M main
git push -u origin main
```

### 2. Deploy to Vercel

1. Go to [vercel.com](https://vercel.com) and sign in with your GitHub account
2. Click "Add New" → "Project"
3. Import your `poker-game-ui` repository
4. Vercel will auto-detect the configuration from `vercel.json`
5. Click "Deploy"

### 3. Important Notes

⚠️ **Model File Issue**: Your `model4.pth` file (the trained poker AI model) might be too large for GitHub (>100MB). You have two options:

**Option A: Git LFS (recommended)**
```bash
# Install Git LFS
git lfs install

# Track the model file
git lfs track "*.pth"

# Add .gitattributes
git add .gitattributes

# Now add and commit the model
git add model4.pth
git commit -m "Add model with Git LFS"
git push
```

**Option B: Host model elsewhere**
Upload `model4.pth` to a cloud storage (Google Drive, Dropbox) and modify `custom_player.py` to download it on first run.

### 4. Environment Variables (if needed)

If you add any secrets later, set them in Vercel:
- Go to your project settings → Environment Variables
- Add variables like `SECRET_KEY`, etc.

## Configuration Files

- `vercel.json` - Vercel deployment configuration
- `requirements.txt` - Python dependencies
- `.gitignore` - Files to exclude from git

## Troubleshooting

**Issue: Build fails due to torch size**
- Torch is large (~800MB). Vercel has deployment size limits.
- Consider using `torch --no-deps` or `torch-cpu` only:
  ```
  torch==2.1.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
  ```

**Issue: Session not persisting**
- Vercel serverless functions are stateless
- The `games` dictionary will reset between requests
- For production, use Redis or a database (Vercel KV, Upstash, etc.)

## Alternative: Free Hosting Platforms

If Vercel doesn't work well (due to torch size), try:

1. **Render.com** (recommended for Flask)
   - Supports persistent storage
   - No serverless limitations
   - Free tier available

2. **Railway.app**
   - Easy Flask deployment
   - Free $5/month credit

3. **PythonAnywhere**
   - Free tier for Flask apps
   - Simple setup
