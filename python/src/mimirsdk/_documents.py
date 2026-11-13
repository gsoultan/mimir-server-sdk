from __future__ import annotations

import builtins
import os
from dataclasses import dataclass, field
from typing import Any, Callable, Iterator, Mapping, Optional, Union

from . import types as t
from ._base import Service, poll
from ._errors import DocumentError
from ._models import ChatMessages, _chat_messages
from ._transport import to_message


@dataclass
class Answer:
    """A whole answer from a collection, as ``ask_text`` collects it."""

    text: str = ""
    sources: list[t.Passage] = field(default_factory=list)
    # False when the answer stopped at the most tokens it may write.
    finished: bool = False
    prompt_tokens: int = 0
    generated_tokens: int = 0
    duration_micros: int = 0


class DocumentService(Service):
    """Answers questions from a team's own files. A collection holds
    documents (PDF, Word, Markdown, web pages or text); the server reads
    each into passages in the background, and ``ask`` answers from the
    passages that best match a question, citing them as [1], [2].

    Apps that speak the OpenAI API can ask a collection too, by sending its
    ``api_name`` as the model to /v1/chat/completions."""

    def list_collections(self) -> builtins.list[t.Collection]:
        """The collections the caller may see, by name."""
        res = self._call("mimir.v1.DocumentService.ListCollections", t.ListCollectionsRequest())
        return list(res.collections)

    def get_collection(self, id: str) -> t.GetCollectionResponse:
        """A collection with its documents, newest first."""
        return self._call("mimir.v1.DocumentService.GetCollection", t.GetCollectionRequest(id=id))

    def create_collection(
        self, request: Union[t.CreateCollectionRequest, Mapping[str, Any], None] = None, **fields: Any
    ) -> t.Collection:
        """Make a collection. ``embedding_model_id`` reads the documents and
        can't change later; ``language_model_id`` writes the answers and
        defaults to the same model."""
        req = to_message(t.CreateCollectionRequest, request, fields)
        return self._call("mimir.v1.DocumentService.CreateCollection", req).collection

    def update_collection(
        self, request: Union[t.UpdateCollectionRequest, Mapping[str, Any], None] = None, **fields: Any
    ) -> t.Collection:
        """Change a collection's name, language model and instructions."""
        req = to_message(t.UpdateCollectionRequest, request, fields)
        return self._call("mimir.v1.DocumentService.UpdateCollection", req).collection

    def delete_collection(self, id: str) -> None:
        """Remove a collection with its documents."""
        self._call("mimir.v1.DocumentService.DeleteCollection", t.DeleteCollectionRequest(id=id))

    def add(self, collection_id: str, name: str, data: bytes) -> t.Document:
        """Add a file's contents to a collection; ``name``'s extension
        (.pdf, .docx, .md, .html, .txt) says how to read it. The server reads
        it in the background: ``wait_document`` follows it."""
        req = t.AddDocumentRequest(collection_id=collection_id, name=name, data=bytes(data))
        return self._call("mimir.v1.DocumentService.AddDocument", req).document

    def add_file(self, collection_id: str, path: Union[str, os.PathLike[str]]) -> t.Document:
        """``add`` for a file on disk."""
        with open(path, "rb") as f:
            data = f.read()
        return self.add(collection_id, os.path.basename(os.fspath(path)), data)

    def get_document(self, id: str) -> t.Document:
        """One document."""
        return self._call("mimir.v1.DocumentService.GetDocument", t.GetDocumentRequest(id=id)).document

    def delete_document(self, id: str) -> None:
        """Remove a document and its passages. One being read can't be
        deleted until it's done."""
        self._call("mimir.v1.DocumentService.DeleteDocument", t.DeleteDocumentRequest(id=id))

    def wait_document(
        self,
        id: str,
        *,
        interval: float = 1.0,
        timeout: Optional[float] = None,
        on_progress: Optional[Callable[[t.Document], Any]] = None,
    ) -> t.Document:
        """Follow a document until it is read or fails. One that fails
        raises DocumentError, which holds the document."""
        from ._training import _ended

        doc = poll(lambda: self.get_document(id), _ended, interval, timeout, on_progress)
        if doc.status != t.JOB_STATUS_SUCCEEDED:
            raise DocumentError(doc)
        return doc

    def search(self, collection_id: str, query: str, limit: int = 0) -> builtins.list[t.Passage]:
        """Up to ``limit`` passages that best match ``query``, best first; 0
        means 5."""
        req = t.SearchRequest(collection_id=collection_id, query=query, limit=limit)
        return list(self._call("mimir.v1.DocumentService.Search", req).passages)

    def ask(
        self,
        request: Union[t.AskRequest, Mapping[str, Any], None] = None,
        *,
        collection_id: str = "",
        messages: Optional[ChatMessages] = None,
        **fields: Any,
    ) -> Iterator[t.AskResponse]:
        """Answer the last question of a chat from a collection's documents,
        yielding the answer as it is written. The first message carries the
        sources the answer cites as [1], [2] and so on; the last has
        ``done`` set::

            for piece in client.documents.ask(collection_id=id, messages=[user_message("Can I return a used item?")]):
                print(piece.text, end="", flush=True)
        """
        req = to_message(t.AskRequest, request, fields)
        if collection_id:
            req.collection_id = collection_id
        if messages is not None:
            _chat_messages(req.messages, messages)
        return self._stream("mimir.v1.DocumentService.Ask", req)

    def ask_text(
        self,
        request: Union[t.AskRequest, Mapping[str, Any], None] = None,
        *,
        collection_id: str = "",
        messages: Optional[ChatMessages] = None,
        **fields: Any,
    ) -> Answer:
        """``ask``, waiting for the whole answer."""
        a = Answer()
        parts = []
        for piece in self.ask(request, collection_id=collection_id, messages=messages, **fields):
            if len(piece.sources):
                a.sources = list(piece.sources)
            parts.append(piece.text)
            if piece.done:
                a.finished = piece.finished
                a.prompt_tokens = piece.prompt_tokens
                a.generated_tokens = piece.generated_tokens
                a.duration_micros = piece.duration_micros
        a.text = "".join(parts)
        return a
