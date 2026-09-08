import re
from app.models.chunk import Chunk
from app.core.logging import logger


class MarkdownChunker:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 150):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(
        self,
        markdown_text: str,
        document_id: str,
        source: str,
    ) -> list[Chunk]:
        """
        Splits structured Markdown text into semantic chunks while maintaining
        heading paths, sections, tables, and offset metadata.
        """
        if not markdown_text or not markdown_text.strip():
            return []

        # Split into header-delimited sections or logical blocks
        lines = markdown_text.splitlines(keepends=True)
        
        current_headings: list[tuple[int, str]] = []  # [(level, text)]
        blocks: list[dict] = []
        current_block_lines: list[str] = []
        current_char_offset = 0
        block_start_char = 0
        current_heading_path: list[str] = []
        current_section: str | None = None

        header_pattern = re.compile(r"^(#{1,6})\s+(.+)$")
        
        for line in lines:
            line_len = len(line)
            match = header_pattern.match(line.strip())
            
            if match:
                # Flush existing block if it has content
                if current_block_lines:
                    text_content = "".join(current_block_lines).strip()
                    if text_content:
                        blocks.append({
                            "text": text_content,
                            "heading_path": list(current_heading_path),
                            "section": current_section,
                            "start_char": block_start_char,
                            "end_char": current_char_offset,
                        })
                    current_block_lines = []
                    block_start_char = current_char_offset

                level = len(match.group(1))
                heading_title = match.group(2).strip()

                # Update heading hierarchy stack
                while current_headings and current_headings[-1][0] >= level:
                    current_headings.pop()
                current_headings.append((level, heading_title))
                
                current_heading_path = [h[1] for h in current_headings]
                current_section = heading_title
                
                # Add heading line as start of new block
                current_block_lines.append(line)
            else:
                if not current_block_lines:
                    block_start_char = current_char_offset
                current_block_lines.append(line)
            
            current_char_offset += line_len

        # Flush trailing block
        if current_block_lines:
            text_content = "".join(current_block_lines).strip()
            if text_content:
                blocks.append({
                    "text": text_content,
                    "heading_path": list(current_heading_path),
                    "section": current_section,
                    "start_char": block_start_char,
                    "end_char": current_char_offset,
                })

        # Now merge or partition blocks into target chunk sizes
        chunks: list[Chunk] = []
        chunk_index = 0

        for block in blocks:
            b_text = block["text"]
            b_path = block["heading_path"]
            b_sec = block["section"]
            b_start = block["start_char"]
            b_end = block["end_char"]

            if len(b_text) <= self.chunk_size:
                chunk_index += 1
                chunks.append(
                    Chunk(
                        id=f"{document_id}_chunk_{chunk_index:03d}",
                        document_id=document_id,
                        text=b_text,
                        source=source,
                        section=b_sec,
                        heading_path=b_path,
                        start_char=b_start,
                        end_char=b_end,
                    )
                )
            else:
                # Split large section into overlapping windows along paragraphs/lines
                sub_chunks = self._split_large_block(
                    text=b_text,
                    base_start=b_start,
                    heading_path=b_path,
                )
                for sub in sub_chunks:
                    chunk_index += 1
                    chunks.append(
                        Chunk(
                            id=f"{document_id}_chunk_{chunk_index:03d}",
                            document_id=document_id,
                            text=sub["text"],
                            source=source,
                            section=b_sec,
                            heading_path=b_path,
                            start_char=sub["start_char"],
                            end_char=sub["end_char"],
                        )
                    )

        logger.info(f"Chunked document '{source}' into {len(chunks)} Markdown-aware chunks")
        return chunks

    def _split_large_block(
        self,
        text: str,
        base_start: int,
        heading_path: list[str],
    ) -> list[dict]:
        """Splits a large text block into overlapping sub-chunks by paragraphs or sentences."""
        paragraphs = text.split("\n\n")
        sub_chunks: list[dict] = []
        current_text = ""
        current_start = base_start
        offset = 0

        context_prefix = ""
        if heading_path:
            context_prefix = f"[{' > '.join(heading_path)}]\n"

        for p in paragraphs:
            p_clean = p.strip()
            if not p_clean:
                offset += len(p) + 2
                continue

            candidate = f"{current_text}\n\n{p_clean}".strip() if current_text else p_clean
            
            if len(candidate) + len(context_prefix) <= self.chunk_size:
                current_text = candidate
            else:
                if current_text:
                    sub_chunks.append({
                        "text": f"{context_prefix}{current_text}".strip(),
                        "start_char": current_start,
                        "end_char": current_start + len(current_text),
                    })
                    # Overlap retention
                    overlap_chars = current_text[-self.chunk_overlap:] if len(current_text) > self.chunk_overlap else ""
                    current_text = f"{overlap_chars}\n\n{p_clean}".strip() if overlap_chars else p_clean
                    current_start = base_start + offset
                else:
                    # Single paragraph exceeds chunk_size: slice by character/sentence
                    sub_chunks.append({
                        "text": f"{context_prefix}{p_clean[:self.chunk_size]}".strip(),
                        "start_char": base_start + offset,
                        "end_char": base_start + offset + min(len(p_clean), self.chunk_size),
                    })
                    current_text = p_clean[self.chunk_size - self.chunk_overlap:].strip()
                    current_start = base_start + offset + self.chunk_size - self.chunk_overlap
            
            offset += len(p) + 2

        if current_text:
            sub_chunks.append({
                "text": f"{context_prefix}{current_text}".strip(),
                "start_char": current_start,
                "end_char": current_start + len(current_text),
            })

        return sub_chunks
