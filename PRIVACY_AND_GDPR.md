
# Privacy & GDPR Compliance

## Overview

JobFinder Pro is designed with privacy and GDPR compliance in mind. This document outlines the privacy features and how to configure them.

## Privacy Features

### 1. Resume Data Storage

By default, raw resume text is **NOT** stored. Instead, the system stores a sanitized version that:

- Removes email addresses
- Removes phone numbers
- Removes physical addresses
- Truncates to a maximum length

To enable raw resume storage (not recommended for production):

```bash
STORE_RESUME_RAW=true
```

### 2. Job Data Anonymization

Job data is anonymized by default before storage:

- Raw API responses are discarded
- URLs are hashed to prevent tracking
- Only essential job information is retained

To disable anonymization (development only):

```bash
ANONYMIZE_JOBS=false
```

### 3. Data Retention

Configure data retention periods for:

- Processed resumes
- Job listings
- Match results

## Configuration

### Environment Variables

```bash
# Privacy Settings
STORE_RESUME_RAW=false        # Don't store raw resume text
ANONYMIZE_JOBS=true           # Anonymize job data
```

## Testing Privacy Features

Run privacy tests:

```bash
pytest tests/test_privacy.py -v
```

## User Rights

The system supports GDPR user rights:

1. **Right to Access**: Users can download their data
2. **Right to Deletion**: Users can delete their account and all associated data
3. **Right to Rectification**: Users can update their information
4. **Right to Data Portability**: Data export in JSON format

## Compliance Checklist

- [ ] STORE_RESUME_RAW is set to `false` in production
- [ ] ANONYMIZE_JOBS is set to `true`
- [ ] Privacy tests pass
- [ ] Data retention policies are configured
- [ ] User consent is obtained before processing
- [ ] Privacy policy is displayed to users
- [ ] Data breach notification procedures are in place

## Security Best Practices

1. Never commit `.env` file
2. Rotate secrets regularly
3. Use HTTPS only in production
4. Implement rate limiting
5. Monitor for suspicious activity
6. Regular security audits
