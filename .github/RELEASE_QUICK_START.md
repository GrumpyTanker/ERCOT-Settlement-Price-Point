# Quick Start: Creating a Release

## TL;DR - Release in 3 Commands

```bash
# 1. Make sure version is updated in manifest.json and CHANGELOG.md
# 2. Create and push tag
git tag v1.1.0
git push origin v1.1.0
# 3. Done! GitHub Actions handles the rest
```

## What Happens Automatically

When you push a version tag (e.g., `v1.1.0`):

✅ GitHub Actions workflow starts  
✅ Validates version matches manifest.json  
✅ Creates release archive (ZIP)  
✅ Creates GitHub Release  
✅ Attaches ZIP file  
✅ Adds release notes from CHANGELOG or release notes file  
✅ Updates `latest` tag  

## Before Tagging

Make sure these are done:

1. **Update manifest.json**:
   ```json
   {
     "version": "1.1.0"
   }
   ```

2. **Update CHANGELOG.md**:
   ```markdown
   ## [1.1.0] - 2025-10-10
   
   ### Added
   - Feature description
   ```

3. **Commit and push**:
   ```bash
   git add custom_components/ercot_spp/manifest.json CHANGELOG.md
   git commit -m "Prepare release v1.1.0"
   git push
   ```

## Create Release

```bash
git tag v1.1.0
git push origin v1.1.0
```

That's it! Check GitHub Releases in ~30 seconds.

## Verify Release

Go to: https://github.com/GrumpyTanker/ERCOT-Settlement-Price-Point/releases

You should see:
- New release `v1.1.0`
- ZIP file attached: `ercot_spp.zip`
- Release notes (from CHANGELOG or release notes file)

## Rollback (if needed)

```bash
# Delete tag locally
git tag -d v1.1.0

# Delete tag on GitHub
git push origin :v1.1.0

# Delete release on GitHub (manual - go to Releases page)
```

## Need More Details?

See [RELEASE_PROCESS.md](RELEASE_PROCESS.md) for:
- Complete step-by-step guide
- Troubleshooting
- Workflow details
- Version numbering guidelines

---

**Quick Reference Card**

| Task | Command |
|------|---------|
| Create tag | `git tag v1.1.0` |
| Push tag | `git push origin v1.1.0` |
| Delete local tag | `git tag -d v1.1.0` |
| Delete remote tag | `git push origin :v1.1.0` |
| View tags | `git tag -l` |
| View release | Check GitHub Releases page |
