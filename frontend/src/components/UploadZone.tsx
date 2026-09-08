import React, { useRef, useState } from "react";
import { UploadCloud, Loader2 } from "lucide-react";
import { uploadDocument } from "../api/client";

interface UploadZoneProps {
  onUploadSuccess: () => void;
}

export const UploadZone: React.FC<UploadZoneProps> = ({ onUploadSuccess }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFiles = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    const file = files[0];

    setIsUploading(true);
    setStatusMessage(`Parsing & chunking ${file.name}...`);

    try {
      const res = await uploadDocument(file);
      setStatusMessage(`Indexed ${res.chunk_count} chunks successfully!`);
      setTimeout(() => setStatusMessage(null), 3000);
      onUploadSuccess();
    } catch (err: any) {
      setStatusMessage(`Error: ${err.message}`);
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFiles(e.dataTransfer.files);
  };

  return (
    <div>
      <input
        type="file"
        ref={fileInputRef}
        onChange={(e) => handleFiles(e.target.files)}
        style={{ display: "none" }}
        accept=".pdf,.docx,.doc,.pptx,.xlsx,.md,.markdown,.txt"
      />
      <div
        className={`upload-card ${isDragging ? "drag-over" : ""}`}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => !isUploading && fileInputRef.current?.click()}
      >
        <div className="upload-icon">
          {isUploading ? <Loader2 className="animate-spin" size={24} /> : <UploadCloud size={24} />}
        </div>
        <div className="upload-text-main">
          {isUploading ? "Processing Document..." : "Upload Document"}
        </div>
        <div className="upload-text-sub">
          {statusMessage || "PDF, DOCX, PPTX, XLSX, Markdown, or Text"}
        </div>
      </div>
    </div>
  );
};
