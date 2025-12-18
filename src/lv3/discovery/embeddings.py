from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


def _require(module: str, *, install_hint: str) -> None:
    try:
        __import__(module)
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(f"Missing dependency `{module}`. {install_hint}\nOriginal error: {exc}") from exc


def l2_normalize(vectors):
    import numpy as np

    vectors = np.asarray(vectors, dtype="float32")
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return vectors / norms


@dataclass(frozen=True)
class SonarConfig:
    encoder: str = "text_sonar_basic_encoder"
    tokenizer: str = "text_sonar_basic_encoder"


class SonarEmbedder:
    def __init__(self, *, config: SonarConfig | None = None):
        self.config = config or SonarConfig()
        self._pipeline = None

    def _get_pipeline(self):
        _require(
            "sonar",
            install_hint="Install optional deps: `python -m pip install -r requirements.embeddings.txt`.",
        )
        from sonar.inference_pipelines.text import TextToEmbeddingModelPipeline

        if self._pipeline is None:
            self._pipeline = TextToEmbeddingModelPipeline(
                encoder=self.config.encoder,
                tokenizer=self.config.tokenizer,
            )
        return self._pipeline

    def embed(self, texts: list[str], *, sonar_lang: str):
        pipeline = self._get_pipeline()
        vecs = pipeline.predict(texts, source_lang=sonar_lang)
        # SONAR returns a numpy array or torch tensor depending on version.
        try:
            import numpy as np

            vecs = np.asarray(vecs)
        except Exception:
            pass
        return l2_normalize(vecs)


@dataclass(frozen=True)
class CanineConfig:
    model_id: str = "google/canine-c"
    pooling: str = "mean"  # "mean" | "cls"


class CanineEmbedder:
    def __init__(self, *, config: CanineConfig | None = None, device: str = "cpu"):
        self.config = config or CanineConfig()
        self.device = device
        self._tokenizer = None
        self._model = None

    def _load(self):
        _require(
            "transformers",
            install_hint="Install optional deps: `python -m pip install -r requirements.embeddings.txt`.",
        )
        _require(
            "torch",
            install_hint="Install optional deps: `python -m pip install -r requirements.embeddings.txt`.",
        )
        import torch
        from transformers import AutoModel, AutoTokenizer

        if self._tokenizer is None:
            self._tokenizer = AutoTokenizer.from_pretrained(self.config.model_id)
        if self._model is None:
            self._model = AutoModel.from_pretrained(self.config.model_id)
            self._model.eval()
            self._model.to(self.device)
        return torch

    def embed(self, texts: list[str]):
        torch = self._load()
        tokenizer = self._tokenizer
        model = self._model
        assert tokenizer is not None and model is not None

        batch = tokenizer(
            texts,
            padding=True,
            truncation=True,
            return_tensors="pt",
        )
        batch = {k: v.to(self.device) for k, v in batch.items()}

        with torch.no_grad():
            outputs = model(**batch)

        last = outputs.last_hidden_state  # [B, T, H]
        if self.config.pooling == "cls":
            pooled = last[:, 0, :]
        else:
            pooled = last.mean(dim=1)

        return l2_normalize(pooled.detach().cpu().numpy())
