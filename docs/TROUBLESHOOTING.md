# Troubleshooting Guide

## Common Issues

### Issue: Module not found error

**Error**: `ModuleNotFoundError: No module named 'whatsapp_backup_manager'`

**Solution**:
1. Ensure you're in the project root directory
2. Activate virtual environment
3. Reinstall package: `pip install -e .`

### Issue: Database locked

**Error**: `sqlite3.OperationalError: database is locked`

**Solution**:
1. Close all running instances
2. Wait a few seconds
3. Delete `*.db-journal` files if they exist
4. Restart application

### Issue: Permission denied on backup directory

**Error**: `PermissionError: [Errno 13] Permission denied`

**Solution**:
1. Check folder permissions
2. On Linux/Mac: `chmod 755 ./backups`
3. Run application with appropriate user

### Issue: Google Drive authentication fails

**Error**: `google.auth.exceptions.DefaultCredentialsError`

**Solution**:
1. Verify `credentials.json` exists
2. Check JSON file is valid
3. Delete `token.pickle` to force re-authentication
4. Re-run application to authorize

## Getting Help

- Check application logs in `./logs/app.log`
- Review GitHub Issues
- Submit detailed bug report with:
  - Error message
  - Stack trace
  - Steps to reproduce
  - System information (OS, Python version)
