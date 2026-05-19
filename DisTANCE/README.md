---
license: apache-2.0
task_categories:
  - visual-question-answering
language:
  - en
tags:
  - multimodal
  - perception
  - benchm
  ark
  - visual-estimation
  - geometry
size_categories:
  - n<1K
---

# DisTANCE: A Perception-Centric Benchmark for Visual Estimation

**DisTANCE** (**Dis**tance reasoning **T**ask with **A**nalytical **N**umeric and **C**omparative **E**stimation) is a benchmark introduced in the paper:

> **Unleashing Perception-Time Scaling to Multimodal Reasoning Models**  
> Yifan Li, Zhenghao Chen, Ziheng Wu, Kun Zhou, Ruipu Luo, Can Zhang, Zhentao He, Yufei Zhan, Wayne Xin Zhao, Minghui Qiu  
> *ICLR 2026* · [arXiv:2510.08964](https://arxiv.org/abs/2510.08964)

---

## Motivation

Recent advances in inference-time scaling — particularly through reinforcement learning with verifiable rewards (RLVR) — have substantially improved the *reasoning* capabilities of Large Vision-Language Models (LVLMs). However, it remains unclear whether such gains transfer to *visual perception*.

DisTANCE is designed to fill this gap. It focuses on **visual estimation**: given a synthetic geometric image, a model must estimate quantitative spatial properties (length, perimeter, area) with numerical precision. Because all answers depend purely on what is visible in the image, the benchmark isolates perceptual competence from general language reasoning, making it a clean probe for the question: *does inference-time scaling help perception?*

Evaluation results reveal that most LVLMs perform poorly — open-source models rarely exceed 35% RA<sub>avg</sub>, and even frontier systems such as Gemini-2.5-Flash reach only 51.9%. Reasoning-enhanced models offer only marginal improvement, a phenomenon the authors attribute to **Fast Perception**: the tendency of LVLMs to express perceptual results in minimal tokens without modeling the underlying perceptual process.

---

## Dataset Overview

| Property | Detail |
|---|---|
| Total samples | 300 |
| Sub-tasks | 3 (Length, Perimeter, Area) |
| Samples per sub-task | 100 |
| Image type | Synthetic (PNG), 600–1200 px |
| Shapes | Circles, triangles, rectangles in varied colors |
| Answer type | Relative numerical estimation (float) |
| Task formulation | Regression (relative estimation to remove resolution bias) |

### Sub-tasks

| Category | Description | Example question |
|---|---|---|
| `1d_length` | Estimate a length ratio between two spatial extents | *"What is the height of the image if the medium side of the red triangle is 1 unit?"* |
| `1d_perimeter` | Estimate a perimeter ratio between two objects | *"Measure the length of the perimeter of the image in relation to the perimeter of the purple circle."* |
| `2d_area` | Estimate an area ratio between two shapes | *"What is the area of the red rectangle relative to the orange rectangle?"* |

---

## Evaluation Metric

DisTANCE uses **Relative Accuracy (RA)**. A prediction $\hat{y}$ is considered correct under threshold $\theta$ if:

$$\frac{|\hat{y} - y|}{y} < \theta$$

Two metrics are reported:

- **RA<sub>avg</sub>**: average accuracy across thresholds $\theta \in \{0.1, 0.2, 0.3, 0.4, 0.5\}$
- **RA<sub>0.1</sub>**: high-precision accuracy at $\theta = 0.1$

---

## Dataset Format

The benchmark is provided as a single Parquet file (`benchmark.parquet`) with images embedded as binary data.

| Column | Type | Description |
|---|---|---|
| `id` | string | Unique identifier, e.g. `eval_1d_length_000001` |
| `category` | string | Sub-task: `1d_length`, `1d_perimeter`, or `2d_area` |
| `problem` | string | Natural language question |
| `answer` | float64 | Ground-truth numerical answer |
| `image` | binary | PNG image bytes embedded directly |

### Loading the Dataset

```python
import pyarrow.parquet as pq
from PIL import Image
import io

table = pq.read_table("benchmark.parquet")
df = table.to_pandas()

# Access a sample
row = df.iloc[0]
print(row["id"])        # eval_1d_length_000001
print(row["category"])  # 1d_length
print(row["problem"])   # question text
print(row["answer"])    # ground-truth float

# Decode the embedded image
image = Image.open(io.BytesIO(row["image"]))
image.show()
```

### Filtering by Sub-task

```python
length_df    = df[df["category"] == "1d_length"]
perimeter_df = df[df["category"] == "1d_perimeter"]
area_df      = df[df["category"] == "2d_area"]
```

### Computing Relative Accuracy

```python
import numpy as np

def relative_accuracy(predictions, targets, threshold=0.1):
    errors = np.abs(predictions - targets) / np.abs(targets)
    return (errors < threshold).mean()

def ra_avg(predictions, targets, thresholds=(0.1, 0.2, 0.3, 0.4, 0.5)):
    return np.mean([relative_accuracy(predictions, targets, t) for t in thresholds])
```

---

## Citation

```bibtex
@inproceedings@article{li2025unleashing,
  title={Unleashing Perception-Time Scaling to Multimodal Reasoning Models},
  author={Li, Yifan and Chen, Zhenghao and Wu, Ziheng and Zhou, Kun and Luo, Ruipu and Zhang, Can and He, Zhentao and Zhan, Yufei and Zhao, Wayne Xin and Qiu, Minghui},
  journal={arXiv preprint arXiv:2510.08964},
  year={2025}
}
```
