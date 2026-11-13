from __future__ import annotations

import builtins
import io
import os
import stat
from dataclasses import dataclass
from typing import IO, Any, Iterable, Iterator, Mapping, Optional, Union

from . import types as t
from ._base import Service
from ._errors import Code, error_for
from ._transport import to_message

UPLOAD_PATH = "/api/uploads"
_CHUNK = 1 << 20

ChatMessages = Iterable[Union[t.ChatMessage, Mapping[str, str]]]


def user_message(content: str) -> t.ChatMessage:
    """A chat turn written by a person."""
    return t.ChatMessage(role="user", content=content)


def assistant_message(content: str) -> t.ChatMessage:
    """A chat turn the model wrote earlier."""
    return t.ChatMessage(role="assistant", content=content)


@dataclass
class ChatReply:
    """A whole chat turn, as ``chat_text`` collects it."""

    text: str = ""
    prompt_tokens: int = 0
    generated_tokens: int = 0
    # The model ended the text itself, rather than running into the token
    # limit.
    finished: bool = False
    duration_micros: int = 0


class ModelService(Service):
    """Manages models and asks them questions."""

    def list(self) -> builtins.list[t.Model]:
        """Every model the caller may see, newest first."""
        return list(self._call("mimir.v1.ModelService.ListModels", t.ListModelsRequest()).models)

    def get(self, id: str) -> t.Model:
        """One model."""
        return self._call("mimir.v1.ModelService.GetModel", t.GetModelRequest(id=id)).model

    def architectures(self) -> builtins.list[t.Architecture]:
        """The model types the server can build and run."""
        res = self._call("mimir.v1.ModelService.ListArchitectures", t.ListArchitecturesRequest())
        return list(res.architectures)

    def create(self, request: Union[t.CreateModelRequest, Mapping[str, Any], None] = None, **fields: Any) -> t.Model:
        """Store a model from its weights held in memory (``weights``), or
        from a file sent beforehand (``upload``). For a file on disk,
        ``upload_file`` is simpler."""
        req = to_message(t.CreateModelRequest, request, fields)
        return self._call("mimir.v1.ModelService.CreateModel", req).model

    def upload(self, name: str, architecture: str, data: Union[bytes, IO[bytes]]) -> t.Model:
        """Store a model whose weights are ``data``: a Mimir Model (.mim)
        file, or an ONNX or GGUF file for the "mim" and language-model
        architectures, which the server converts. A file object is streamed
        to the server as it is read, so it can be larger than memory; the
        server's -max-model-mb caps it."""
        if isinstance(data, (bytes, bytearray, memoryview)):
            data = io.BytesIO(bytes(data))
        upload_id = self._send(data, _size_of(data))
        return self.create(t.CreateModelRequest(name=name, architecture=architecture, upload=upload_id))

    def upload_file(self, path: Union[str, os.PathLike[str]], architecture: str, name: str = "") -> t.Model:
        """``upload`` from a file. An empty name uses the file's name
        without its extension."""
        if not name:
            name = os.path.splitext(os.path.basename(os.fspath(path)))[0]
        with open(path, "rb") as f:
            return self.upload(name, architecture, f)

    def _send(self, f: IO[bytes], size: int) -> str:
        def chunks() -> Iterator[bytes]:
            while True:
                b = f.read(_CHUNK)
                if not b:
                    return
                yield b

        out = self._t.upload(UPLOAD_PATH, chunks(), size)
        upload_id = out.get("upload") if isinstance(out, dict) else None
        if not upload_id:
            raise error_for(Code.INTERNAL, f"the server's answer has no upload id: {out!r}", UPLOAD_PATH)
        return str(upload_id)

    def save_architecture(
        self, request: Union[t.SaveArchitectureRequest, Mapping[str, Any], None] = None, **fields: Any
    ) -> t.Architecture:
        """Describe a model type written in someone's own code and run on
        workers, or change how one already saved is described."""
        req = to_message(t.SaveArchitectureRequest, request, fields)
        return self._call("mimir.v1.ModelService.SaveArchitecture", req).architecture

    def delete_architecture(self, name: str) -> None:
        """Remove a described model type that no model uses."""
        self._call("mimir.v1.ModelService.DeleteArchitecture", t.DeleteArchitectureRequest(name=name))

    def update(self, request: Union[t.UpdateModelRequest, Mapping[str, Any], None] = None, **fields: Any) -> t.Model:
        """Rename a model, change its description or language settings, or
        let it run on people's devices."""
        req = to_message(t.UpdateModelRequest, request, fields)
        return self._call("mimir.v1.ModelService.UpdateModel", req).model

    def delete(self, id: str) -> None:
        """Remove a model and its weights."""
        self._call("mimir.v1.ModelService.DeleteModel", t.DeleteModelRequest(id=id))

    def set_worker(self, id: str, worker_id: str) -> t.Model:
        """Pick the worker that answers a model, or "" for automatic."""
        req = t.SetModelWorkerRequest(id=id, worker_id=worker_id)
        return self._call("mimir.v1.ModelService.SetModelWorker", req).model

    def download(self, id: str) -> t.GetDeviceModelResponse:
        """A model that may run on people's devices, with its stored
        weights."""
        return self._call("mimir.v1.ModelService.GetDeviceModel", t.GetDeviceModelRequest(id=id))

    def versions(self, model_id: str) -> builtins.list[t.ModelVersion]:
        """A model's stored versions, newest first. The live one, which
        answers predictions, has ``live`` set."""
        res = self._call("mimir.v1.ModelService.ListModelVersions", t.ListModelVersionsRequest(model_id=model_id))
        return list(res.versions)

    def use_version(self, model_id: str, version_id: str) -> t.Model:
        """Make one of a model's versions the live one, to roll back to an
        earlier version or forward to a newer one."""
        req = t.UseModelVersionRequest(model_id=model_id, version_id=version_id)
        return self._call("mimir.v1.ModelService.UseModelVersion", req).model

    def quality(self, model_id: str, days: int = 0) -> t.GetModelQualityResponse:
        """How a model does in use: its answers and the feedback on them for
        each of the last days (30 when days is 0, at most 365), the last 7
        days' accuracy by that feedback, and whether it has dropped well
        below the model's score when trained."""
        req = t.GetModelQualityRequest(model_id=model_id, days=days)
        return self._call("mimir.v1.ModelService.GetModelQuality", req)

    # Questions.

    def predict(
        self, request: Union[t.PredictRequest, Mapping[str, Any], None] = None, **fields: Any
    ) -> t.PredictResponse:
        """Run one example through a model: a tensor, a table row
        (``fields``) or a photo, depending on what the model reads."""
        return self._call("mimir.v1.PredictService.Predict", to_message(t.PredictRequest, request, fields))

    def predict_fields(self, model_id: str, fields: Mapping[str, Any]) -> t.PredictResponse:
        """Ask a model taught from a table about one row, given by column
        name."""
        req = t.PredictRequest(model_id=model_id, fields={k: str(v) for k, v in fields.items()})
        return self._call("mimir.v1.PredictService.Predict", req)

    def predict_photo(self, model_id: str, photo: bytes) -> t.PredictResponse:
        """Ask a model that looks at photos about one JPG, PNG or GIF."""
        return self._call("mimir.v1.PredictService.Predict", t.PredictRequest(model_id=model_id, photo=photo))

    def send_feedback(self, prediction_id: str, label: str) -> bool:
        """Tell the server what a picking model's answer should have been:
        ``prediction_id`` is ``PredictResponse.prediction_id``, ``label``
        the right answer. Returns whether the model got it right. Sending
        feedback again replaces the earlier one. Answers are kept for
        feedback for 30 days; after that it raises NotFoundError."""
        req = t.SendFeedbackRequest(prediction_id=prediction_id, label=label)
        return self._call("mimir.v1.PredictService.SendFeedback", req).correct

    def send_feedback_value(self, prediction_id: str, value: float) -> bool:
        """``send_feedback`` for a model that answers with a number. The
        answer counts as right within 10% of value, or 0.1 of it when value
        is 0."""
        req = t.SendFeedbackRequest(prediction_id=prediction_id, value=value)
        return self._call("mimir.v1.PredictService.SendFeedback", req).correct

    def explain(self, model_id: str, fields: Mapping[str, Any], label: str = "") -> t.ExplainResponse:
        """Why a model taught on a table gave its answer for one row: each
        column's effect on it, against a typical row. For a model that
        picks, ``label`` names the answer to explain (empty for the one it
        gave) and effects are in chance of that answer (0.12 is 12 points);
        for one that answers with a number they are in its units. The
        effects add up to ``value`` minus ``typical``."""
        req = t.ExplainRequest(model_id=model_id, fields={k: str(v) for k, v in fields.items()}, label=label)
        return self._call("mimir.v1.PredictService.Explain", req)

    def explain_model(self, model_id: str) -> t.ExplainModelResponse:
        """Which columns matter most to a model taught on a table: the
        average size of each column's effect over up to 24 of its recent
        questions, or of the examples it learned from when it has none."""
        return self._call("mimir.v1.PredictService.ExplainModel", t.ExplainModelRequest(model_id=model_id))

    # Language models.

    def generate(
        self, request: Union[t.GenerateRequest, Mapping[str, Any], None] = None, **fields: Any
    ) -> t.GenerateResponse:
        """Continue a prompt with a language model and return the whole
        text at once."""
        return self._call("mimir.v1.PredictService.Generate", to_message(t.GenerateRequest, request, fields))

    def generate_stream(
        self, request: Union[t.GenerateStreamRequest, Mapping[str, Any], None] = None, **fields: Any
    ) -> Iterator[t.GenerateStreamResponse]:
        """``generate``, yielding the text as the model writes it. The last
        piece has ``done`` set and the token counts."""
        req = to_message(t.GenerateStreamRequest, request, fields)
        return self._stream("mimir.v1.PredictService.GenerateStream", req)

    def chat(
        self,
        request: Union[t.ChatRequest, Mapping[str, Any], None] = None,
        *,
        model_id: str = "",
        messages: Optional[ChatMessages] = None,
        **fields: Any,
    ) -> Iterator[t.ChatResponse]:
        """Write a language model's next turn in a chat, yielding the text
        as the model writes it. The last piece has ``done`` set and the
        token counts::

            for piece in client.models.chat(model_id=id, messages=[user_message("Hello!")]):
                print(piece.text, end="", flush=True)

        Breaking out of the loop stops the model."""
        return self._stream("mimir.v1.PredictService.Chat", _chat_request(request, model_id, messages, fields))

    def chat_text(
        self,
        request: Union[t.ChatRequest, Mapping[str, Any], None] = None,
        *,
        model_id: str = "",
        messages: Optional[ChatMessages] = None,
        **fields: Any,
    ) -> ChatReply:
        """``chat``, waiting for the whole answer."""
        reply = ChatReply()
        parts = []
        for piece in self.chat(request, model_id=model_id, messages=messages, **fields):
            parts.append(piece.text)
            if piece.done:
                reply.prompt_tokens = piece.prompt_tokens
                reply.generated_tokens = piece.generated_tokens
                reply.finished = piece.finished
                reply.duration_micros = piece.duration_micros
        reply.text = "".join(parts)
        return reply


def _chat_request(
    request: Union[t.ChatRequest, Mapping[str, Any], None],
    model_id: str,
    messages: Optional[ChatMessages],
    fields: dict[str, Any],
) -> t.ChatRequest:
    req = to_message(t.ChatRequest, request, fields)
    if model_id:
        req.model_id = model_id
    if messages is not None:
        _chat_messages(req.messages, messages)
    return req


def _chat_messages(field: Any, messages: ChatMessages) -> None:
    """Replace a repeated ChatMessage field with messages, which may be
    ChatMessages or dicts with role and content."""
    del field[:]
    for m in messages:
        field.append(m if isinstance(m, t.ChatMessage) else t.ChatMessage(**m))


def _size_of(f: IO[bytes]) -> int:
    """f's remaining length when it can tell without reading it, else -1."""
    try:
        if isinstance(f, io.BytesIO):
            return len(f.getbuffer()) - f.tell()
        st = os.fstat(f.fileno())
        if stat.S_ISREG(st.st_mode):
            return st.st_size - f.tell()
    except (AttributeError, OSError, ValueError, io.UnsupportedOperation):
        pass
    return -1
