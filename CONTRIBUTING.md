# Contributing

感谢你的关注！/ Thanks for your interest!

## Ground Rules

- **小范围改动**：一个 PR 只做一件事
- **向后兼容**：不破坏已有用户的安装
- **命名空间**：所有新文件以 `hypothesis-tracker-` 开头
- **跑通检查**：提交前确保 `python scripts/check_setup.py` 通过

## Good Contributions

- Bug 修复
- 安装器改进（新平台支持、错误提示优化）
- 文档和翻译
- 新的证据信号类型
- 假设模板改进

## Out of Scope

- 券商/交易所 API 集成
- 自动交易执行
- 纯 GUI 功能
- 需要付费 API 的默认功能

## Release Process

1. 更新 `VERSION`
2. 更新 `CHANGELOG.md`
3. 更新文档中的版本号
4. 提交到 `main`
5. 创建 annotated tag：`git tag -a v1.0.0 -m "Release v1.0.0"`
6. Push：`git push origin main && git push origin v1.0.0`
