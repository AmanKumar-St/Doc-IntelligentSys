import React, { useState, useEffect } from "react";
import { Navbar } from "./components/Navbar";
import { UploadZone } from "./components/UploadZone";
import { DocumentList } from "./components/DocumentList";
import { ChatWindow } from "./components/ChatWindow";
import { SearchTab } from "./components/SearchTab";
import { CitationInspector } from "./components/CitationInspector";
import type { DocumentItem, Citation, SystemHealth } from "./types";
import { fetchDocuments, checkHealth } from "./api/client";

export const App: React.FC = () => {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"chat" | "search">("chat");
  const [inspectingCitation, setInspectingCitation] = useState<Citation | null>(null);

  const loadData = async () => {
    try {
      const [h, docs] = await Promise.all([
        checkHealth().catch(() => null),
        fetchDocuments().catch(() => []),
      ]);
      setHealth(h);
      setDocuments(docs);
    } catch (e) {
      console.error("Initial load error", e);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="app-container">
      <Navbar health={health} activeTab={activeTab} setActiveTab={setActiveTab} />

      <div className="workspace-grid">
        {/* Left Sidebar: Upload and Document Catalog */}
        <aside className="sidebar">
          <UploadZone onUploadSuccess={loadData} />
          <DocumentList
            documents={documents}
            selectedDocId={selectedDocId}
            onSelectDoc={setSelectedDocId}
            onRefresh={loadData}
          />
        </aside>

        {/* Main Content Area */}
        <main style={{ display: "flex", flexDirection: "column", height: "100%", overflow: "hidden" }}>
          {activeTab === "chat" ? (
            <ChatWindow
              selectedDocId={selectedDocId}
              onCitationClick={(c) => setInspectingCitation(c)}
            />
          ) : (
            <SearchTab
              selectedDocId={selectedDocId}
              onCitationClick={(c) => setInspectingCitation(c)}
            />
          )}
        </main>
      </div>

      {/* Interactive Citation Drawer */}
      <CitationInspector
        citation={inspectingCitation}
        onClose={() => setInspectingCitation(null)}
      />
    </div>
  );
};

export default App;
