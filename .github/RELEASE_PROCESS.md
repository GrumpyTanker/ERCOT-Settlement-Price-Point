# Release Process

This document describes how to create and publish a new release of the ERCOT Real-Time SPP integration.

## Overview

The release process is automated through GitHub Actions. When you push a version tag, the workflow automatically:
- Validates the version matches manifest.json
- Creates a GitHub Release
- Generates a release archive (ZIP file)
- Attaches release notes
- Updates the `latest` tag

## Prerequisites

Before creating a release, ensure:

1. **Version is updated** in `custom_components/ercot_spp/manifest.json`
2. **CHANGELOG.md** is updated with release notes and date
3. **Release notes** exist (optional): `.github/RELEASE_NOTES_v{version}.md`
4. **All changes are committed** and pushed to main branch
5. **Tests pass** (if applicable)

## Creating a Release

### Method 1: Using Git Tags (Recommended)

1. **Update version files** (if not already done):
   ```bash
   # Update manifest.json version
   # Update CHANGELOG.md with release date
   # Commit changes
   git add custom_components/ercot_spp/manifest.json CHANGELOG.md
   git commit -m "Prepare release v1.1.0"
   git push
   ```

2. **Create and push the version tag**:
   ```bash
   git tag v1.1.0
   git push origin v1.1.0
   ```

3. **GitHub Actions automatically**:
   - Validates the version
   - Creates the release
   - Uploads the integration ZIP file
   - Adds release notes

### Method 2: Using GitHub UI

1. Go to the repository on GitHub
2. Click **Releases** → **Draft a new release**
3. Click **Choose a tag** → Type new tag (e.g., `v1.1.0`)
4. Select **Create new tag: v1.1.0 on publish**
5. Set **Release title**: `Release v1.1.0`
6. Add **Release notes** (or reference `.github/RELEASE_NOTES_v1.1.0.md`)
7. Click **Publish release**

The workflow will still run and attach the ZIP file.

### Method 3: Manual Workflow Dispatch

1. Go to **Actions** → **Create Release**
2. Click **Run workflow**
3. Enter the version (e.g., `v1.1.0`)
4. Click **Run workflow**

## Version Numbering

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR** version (X.0.0): Incompatible API changes
- **MINOR** version (0.X.0): New features, backward compatible
- **PATCH** version (0.0.X): Bug fixes, backward compatible

Examples:
- `v1.0.0` → Initial release
- `v1.1.0` → New features added
- `v1.1.1` → Bug fixes
- `v2.0.0` → Breaking changes

## File Checklist

Before releasing, verify these files are updated:

### Required Files

- [ ] `custom_components/ercot_spp/manifest.json` - Version field
- [ ] `CHANGELOG.md` - New section with version and date
- [ ] All code changes committed and pushed

### Optional Files

- [ ] `.github/RELEASE_NOTES_v{version}.md` - Detailed release notes
- [ ] `README.md` - Any documentation updates
- [ ] `hacs.json` - If HACS metadata changes

## Release Workflow Details

The release workflow (`.github/workflows/release.yml`) performs these steps:

1. **Checkout code** - Gets the repository content
2. **Get version** - Extracts version from tag or input
3. **Verify version** - Confirms tag matches manifest.json
4. **Extract notes** - Finds release notes file (if exists)
5. **Create archive** - Zips the integration files
6. **Generate changelog** - Extracts relevant CHANGELOG section
7. **Create release** - Publishes GitHub Release with artifacts
8. **Update latest tag** - Moves `latest` tag to new release

## What Gets Released

Each release includes:

1. **GitHub Release** with:
   - Version tag (e.g., `v1.1.0`)
   - Release title
   - Release notes/changelog
   - Release date

2. **Release Assets**:
   - `ercot_spp.zip` - Complete integration ready for manual installation

## After Release

1. **Verify the release**:
   - Check GitHub Releases page
   - Download and test the ZIP file
   - Verify release notes are correct

2. **Announce the release** (optional):
   - Home Assistant Community Forum
   - Social media
   - Project discussions

3. **Update HACS** (if applicable):
   - HACS automatically detects new releases via tags
   - No manual action needed for HACS custom repository users

## Troubleshooting

### Workflow fails with "version mismatch"

**Problem**: Tag version doesn't match manifest.json version

**Solution**:
```bash
# Fix manifest.json
vim custom_components/ercot_spp/manifest.json
# Update version field to match tag

# Commit and push
git add custom_components/ercot_spp/manifest.json
git commit -m "Fix version in manifest.json"
git push

# Delete and recreate tag
git tag -d v1.1.0
git push origin :v1.1.0
git tag v1.1.0
git push origin v1.1.0
```

### Release created but ZIP missing

**Problem**: Archive creation failed

**Solution**:
- Check workflow logs in GitHub Actions
- Verify `custom_components/ercot_spp/` directory structure
- Manually trigger workflow dispatch if needed

### Release notes not showing

**Problem**: Release notes file not found

**Solution**:
1. Create `.github/RELEASE_NOTES_v{version}.md`
2. Or workflow will extract from CHANGELOG.md automatically
3. Or edit release on GitHub to add notes manually

## Example: Complete Release Flow

```bash
# 1. Update version in manifest.json to 1.2.0
vim custom_components/ercot_spp/manifest.json

# 2. Update CHANGELOG.md
vim CHANGELOG.md
# Add:
# ## [1.2.0] - 2025-10-15
# ### Added
# - New feature X
# ### Fixed
# - Bug Y

# 3. Commit changes
git add custom_components/ercot_spp/manifest.json CHANGELOG.md
git commit -m "Prepare release v1.2.0"
git push

# 4. Create and push tag
git tag v1.2.0
git push origin v1.2.0

# 5. Wait for GitHub Actions to complete (~30 seconds)

# 6. Verify release at:
# https://github.com/GrumpyTanker/ERCOT-Settlement-Price-Point/releases
```

## Questions?

- Open an issue on GitHub
- Check GitHub Actions logs for workflow details
- Review existing releases for examples

---

**Last Updated**: 2025-10-10  
**Workflow Version**: 1.0
