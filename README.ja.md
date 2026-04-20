[![yamlsan](docs/header.svg)](https://github.com/izag8216/yamlsan)

[English](./README.md) | [Japanese](./README.ja.md)

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](./LICENSE)
[![Tests](https://img.shields.io/badge/Tests-pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)](./tests)

</div>

**yamlsan** はMarkdownファイルのYAML frontmatterを、ユーザー定義スキーマに対して検証するCLIツールです。Obsidian vault、ブログ、ドキュメントのフィールド整合性を保ちます。

## 特徴

- **スキーマ駆動検証** -- YAML/JSONで必須フィールド、型、許可値、正規表現パターンを定義
- **自動修正** -- 欠落フィールドにデフォルト値を適用（`--dry-run`でプレビュー）
- **CI対応** -- `--ci`フラグで最小出力＋適切な終了コード
- **再帰スキャン** -- ディレクトリを指定すれば全`.md`ファイルを検証
- **リッチ出力** -- エラー/警告を色分けしたテーブル表示
- **完全オフライン** -- 外部API不要、アカウント不要、クラウド不要

## インストール

```bash
pip install yamlsan
```

ソースから:

```bash
git clone https://github.com/izag8216/yamlsan.git
cd yamlsan
pip install -e .
```

## クイックスタート

### 1. スキーマを作成

```yaml
# schema.yaml
fields:
  title:
    type: string
    required: true
  created:
    type: date
    required: true
    pattern: "^\\d{4}-\\d{2}-\\d{2}$"
  status:
    type: string
    required: true
    allowed: ["draft", "published", "archived"]
  tags:
    type: list
    required: false
    min_length: 1
  priority:
    type: integer
    required: false
    min_value: 1
    max_value: 5
    default: 3
```

### 2. ファイルを検証

```bash
yamlsan validate ./vault/ --schema schema.yaml
```

### 3. CIで使用

```bash
yamlsan validate --ci ./docs/ --schema schema.yaml
# 終了コード: 0=全件有効, 1=違反あり, 2=エラー
```

### 4. 自動修正

```bash
# 変更をプレビュー
yamlsan fix ./vault/ --schema schema.yaml --dry-run

# デフォルト値を適用
yamlsan fix ./vault/ --schema schema.yaml
```

## スキーマリファレンス

`fields`マッピングの各フィールドがサポートするプロパティ:

| プロパティ | 型 | デフォルト | 説明 |
|-----------|-----|----------|------|
| `type` | string | `"any"` | `string`, `integer`, `float`, `boolean`, `list`, `date`, `enum`, `any` |
| `required` | boolean | `true` | フィールドの必須/任意 |
| `allowed` | list | -- | 許可される値（列挙型） |
| `pattern` | string | -- | 値が一致すべき正規表現パターン |
| `default` | any | -- | 自動修正用のデフォルト値 |
| `min_length` | integer | -- | 文字列/リストの最小長 |
| `max_length` | integer | -- | 文字列/リストの最大長 |
| `min_value` | number | -- | 数値の最小値 |
| `max_value` | number | -- | 数値の最大値 |
| `severity` | string | `"error"` | `"error"` または `"warning"` |

## 終了コード

| コード | 意味 |
|------|------|
| 0 | 全ファイル有効（またはヘルプ/バージョン） |
| 1 | 検証違反あり |
| 2 | 実行時エラー（ファイル未検出、スキーマ不正） |

## 開発

```bash
pip install -e ".[dev]"
pytest --cov=yamlsan
```

## ライセンス

MIT License -- 詳細は[LICENSE](./LICENSE)を参照。
