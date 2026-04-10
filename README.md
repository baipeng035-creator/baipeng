# Marketing Graph Builder (GEO)

一个轻量程序：输入品牌分析报告 + 意图问题，输出营销图谱（JSON/CSV）。

## 功能
- 从品牌报告中提取营销图谱基础节点（卖点、场景、痛点、竞品）
- 将意图问题映射到对应节点，建立 `MENTIONS` 关系
- 输出：
  - `marketing_graph.json`
  - `nodes.csv`
  - `edges.csv`

## 快速开始

```bash
python marketing_graph_builder.py \
  --brand-name "婺女洲度假区" \
  --report-file sample_report.txt \
  --questions-file sample_questions.txt \
  --out-dir output
```

## 输入格式

### 1) 品牌报告（txt）
任意中文文本。

### 2) 意图问题（txt）
每行一个问题。程序会自动筛选包含 `？` 或 `?` 的行。

## 输出说明
- `nodes.csv`: 节点表，字段 `id,type,name,attrs`
- `edges.csv`: 关系表，字段 `source,target,type,attrs`
- `marketing_graph.json`: 全量图数据 + 统计

## 可扩展方向
- 用 LLM 替代关键词抽取（结构化 JSON 输出）
- 增加置信度评分 `confidence`
- 导出 Neo4j Cypher 或 GraphML
