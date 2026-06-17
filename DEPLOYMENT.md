# Streamlit Cloud Deployment Guide

## Common Issues & Fixes

### Issue: "connection refused" Error on Streamlit Cloud

This error occurs when the Streamlit app fails to start properly. The most common causes are:

1. **NLTK resource download failures** - The app tries to download NLP resources that timeout
2. **Missing data file** - The dataset file doesn't exist and generation fails
3. **Import errors** - Module initialization errors that crash the startup

## Solutions Applied

### 1. ✅ Fixed `.streamlit/config.toml`
- Updated port to 8501 (standard Streamlit port)
- Added proper logging configuration
- Configured headless mode for cloud deployment

### 2. ✅ Improved `nlp_processor.py`
- Added robust NLTK resource handling with fallback logic
- Added timeout handling for downloads
- Added warning system instead of hard failures

### 3. ✅ Enhanced Error Handling in `app.py`
- Added try-catch blocks for initialization
- Added logging for debugging
- Better error messages displayed to users
- Graceful degradation if NLTK resources unavailable

### 4. ✅ Created `init_app.py`
- Pre-initialization script
- Can be run manually to prepare environment
- Generates sample dataset if needed

## Deployment Steps

### Option 1: Deploy Directly to Streamlit Cloud (Recommended)

1. Push your code to GitHub
2. Go to [https://share.streamlit.io](https://share.streamlit.io)
3. Click "New app"
4. Select your repository, branch, and `app.py` as the main file
5. The app will deploy and start immediately

Streamlit Cloud will automatically:
- Install all dependencies from `requirements.txt` or `pyproject.toml`
- Download NLTK resources
- Generate the initial dataset on first run

### Option 2: Pre-generate Dataset (Optional)

If deployment fails due to dataset generation timeouts:

1. Locally run: `python init_app.py`
2. This generates the `data/it_job_postings.csv` file
3. Commit this file to GitHub
4. Re-deploy to Streamlit Cloud

### Option 3: Skip Dataset Generation

Edit `app.py` and remove the dataset generation code if you have a pre-generated CSV file.

## Expected Startup Behavior

**First Time (without pre-generated data):**
- Streamlit Cloud fetches code and dependencies (~2-3 min)
- App starts and displays "Generating sample dataset..." message
- Dataset generation happens (takes ~30-60 seconds)
- App becomes fully functional

**Subsequent Runs:**
- Dataset already exists, so app starts immediately (~10-15 seconds)
- Full functionality available

## Troubleshooting

### If app still shows "connection refused":

1. **Check Streamlit Cloud logs** - Look for specific error messages
2. **Check for import errors** - Any missing packages should be visible in logs
3. **Verify `pyproject.toml` or `requirements.txt`** - Ensure all dependencies are listed
4. **Try with pre-generated dataset** - Run `python init_app.py` locally and commit data file

### If app is slow to start:

- This is normal for first deployment (downloading ~64 Python packages + NLTK data)
- Subsequent redeployments should be faster
- Dataset generation takes ~1 minute on first run only

### If charts don't display:

- The app generates them on demand - wait a moment
- Check browser console for any JavaScript errors
- Try refreshing the page

## Performance Notes

- Initial deployment: 3-5 minutes (includes package installation)
- Subsequent deployments: 30-60 seconds
- First app load: 1-2 minutes (includes dataset generation if needed)
- Normal app loads: 5-10 seconds

## Size Limits

- Streamlit Cloud free tier allows up to 1 GB of storage
- Our generated dataset: ~20-30 MB
- All dependencies and NLTK data: ~500 MB
- Plenty of room for additional resources

## Support

If you encounter issues:
1. Check the Streamlit Cloud deployment logs
2. Run `python init_app.py` locally to verify everything works
3. Check [Streamlit Community Forum](https://discuss.streamlit.io/)
