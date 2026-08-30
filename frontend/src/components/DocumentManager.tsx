import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Upload, FileText, Trash2, RefreshCw, ChevronRight,
  CheckCircle, Clock, AlertCircle, Loader, X,
  FileSearch, ArrowLeft, Database, HardDrive, Hash, MessageSquare,
} from 'lucide-react';
import { PolicyQA } from './PolicyQA';

// ── Types ────────────────────────────────────────────────────────────────────
interface DocRecord {
  id:            string;
  original_name: string;
  status:        'pending' | 'processing' | 'indexed' | 'failed';
  page_count:    number | null;
  chunk_count:   number | null;
  file_size:     number | null;
  error_message: string | null;
  uploaded_at:   string;
  processed_at:  string | null;
}

interface Chunk {
  id:          string;
  page_number: number;
  chunk_index: number;
  section:     string | null;
  char_count:  number;
  text:        string;
}

// ── Helpers ──────────────────────────────────────────────────────────────────

/** Returns headers with the admin auth key read from localStorage. */
const adminHeaders = (): Record<string, string> => ({
  'X-Admin-Key': localStorage.getItem('adminKey') ?? 'tata-mitra-admin-2024',
});

const fmtBytes = (b: number | null): string => {
  if (!b) return '—';
  if (b < 1024)       return `${b} B`;
  if (b < 1024 * 1024) return `${(b / 1024).toFixed(1)} KB`;
  return `${(b / 1024 / 1024).toFixed(1)} MB`;
};

const fmtDate = (s: string | null): string => {
  if (!s) return '—';
  return new Date(s).toLocaleString('en-IN', { dateStyle: 'short', timeStyle: 'short' });
};

// ── Status badge ─────────────────────────────────────────────────────────────
function StatusBadge({ status }: { status: DocRecord['status'] }) {
  const cfg = {
    pending:    { label: 'Pending',    icon: Clock,       cls: 'bg-gray-700 text-gray-300' },
    processing: { label: 'Processing', icon: Loader,      cls: 'bg-blue-900/60 text-blue-300 animate-pulse' },
    indexed:    { label: 'Indexed',    icon: CheckCircle, cls: 'bg-emerald-900/60 text-emerald-300' },
    failed:     { label: 'Failed',     icon: AlertCircle, cls: 'bg-red-900/60 text-red-300' },
  }[status];
  const Icon = cfg.icon;
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${cfg.cls}`}>
      <Icon className="w-3 h-3" />
      {cfg.label}
    </span>
  );
}

// ── Chunk Preview Modal ───────────────────────────────────────────────────────
function ChunkModal({ doc, onClose }: { doc: DocRecord; onClose: () => void }) {
  const [chunks, setChunks]   = useState<Chunk[]>([]);
  const [total, setTotal]     = useState(0);
  const [page, setPage]       = useState(1);
  const [loading, setLoading] = useState(false);
  const PAGE_SIZE = 5;

  const loadChunks = async (p: number) => {
    setLoading(true);
    try {
      const res  = await fetch(`/admin/documents/${doc.id}/chunks?page=${p}&page_size=${PAGE_SIZE}`, {
        headers: adminHeaders(),
      });
      const data = await res.json();
      setChunks(data.chunks);
      setTotal(data.total_chunks);
      setPage(p);
    } catch (_) {}
    setLoading(false);
  };

  useEffect(() => { loadChunks(1); }, []);

  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
      <motion.div
        initial={{ opacity: 0, scale: 0.96 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-2xl max-h-[85vh] flex flex-col bg-gray-900 border border-gray-700 rounded-3xl shadow-2xl overflow-hidden"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-5 border-b border-gray-800">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <FileSearch className="w-5 h-5 text-indigo-400" />
              Chunk Preview
            </h2>
            <p className="text-sm text-gray-400 mt-0.5 truncate max-w-xs">{doc.original_name}</p>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-xs text-gray-500">{total} chunks total</span>
            <button onClick={onClose} className="p-2 hover:bg-gray-800 rounded-xl transition-colors">
              <X className="w-5 h-5 text-gray-400" />
            </button>
          </div>
        </div>

        {/* Chunks */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader className="w-6 h-6 text-indigo-400 animate-spin" />
            </div>
          ) : chunks.map((ch) => (
            <div key={ch.id} className="bg-gray-800 border border-gray-700 rounded-2xl p-4">
              <div className="flex items-center gap-3 mb-2 text-xs text-gray-500">
                <span className="bg-indigo-900/50 text-indigo-300 px-2 py-0.5 rounded-full">
                  Chunk #{ch.chunk_index}
                </span>
                <span>Page {ch.page_number}</span>
                <span>{ch.char_count} chars</span>
                {ch.section && (
                  <span className="bg-purple-900/40 text-purple-300 px-2 py-0.5 rounded-full truncate max-w-[120px]">
                    {ch.section}
                  </span>
                )}
              </div>
              <p className="text-sm text-gray-300 leading-relaxed">{ch.text}</p>
            </div>
          ))}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between p-4 border-t border-gray-800">
            <button
              disabled={page <= 1 || loading}
              onClick={() => loadChunks(page - 1)}
              className="px-4 py-2 text-sm rounded-xl bg-gray-800 text-white disabled:opacity-40 hover:bg-gray-700 transition-colors"
            >
              ← Prev
            </button>
            <span className="text-xs text-gray-500">Page {page} of {totalPages}</span>
            <button
              disabled={page >= totalPages || loading}
              onClick={() => loadChunks(page + 1)}
              className="px-4 py-2 text-sm rounded-xl bg-gray-800 text-white disabled:opacity-40 hover:bg-gray-700 transition-colors"
            >
              Next →
            </button>
          </div>
        )}
      </motion.div>
    </div>
  );
}

// ── Main Component ────────────────────────────────────────────────────────────
export const DocumentManager = () => {
  const navigate             = useNavigate();
  const fileInputRef         = useRef<HTMLInputElement>(null);
  const [docs, setDocs]      = useState<DocRecord[]>([]);
  const [loading, setLoading]           = useState(true);
  const [uploading, setUploading]       = useState(false);
  const [processingId, setProcessingId] = useState<string | null>(null);
  const [previewDoc, setPreviewDoc]     = useState<DocRecord | null>(null);
  const [toast, setToast]               = useState<{ msg: string; type: 'success' | 'error' } | null>(null);
  const [isDragOver, setIsDragOver]     = useState(false);
  const [activeTab, setActiveTab]       = useState<'documents' | 'qa'>('documents');

  // Auth guard
  useEffect(() => {
    if (!localStorage.getItem('isAdmin')) navigate('/admin');
    else fetchDocs();
  }, []);

  const showToast = (msg: string, type: 'success' | 'error' = 'success') => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 4000);
  };

  const fetchDocs = async () => {
    setLoading(true);
    try {
      const res  = await fetch('/admin/documents', { headers: adminHeaders() });
      const data = await res.json();
      setDocs(data.documents || []);
    } catch (_) {
      showToast('Failed to load documents', 'error');
    }
    setLoading(false);
  };

  // ── Upload ─────────────────────────────────────────────────────────────────
  const handleFileSelect = (file: File) => {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      showToast('Only PDF files are supported', 'error');
      return;
    }
    uploadFile(file);
  };

  const uploadFile = async (file: File) => {
    setUploading(true);
    const form = new FormData();
    form.append('file', file);

    try {
      const res  = await fetch('/admin/documents/upload', {
        method:  'POST',
        headers: adminHeaders(),
        body:    form,
      });
      const data = await res.json();

      if (!res.ok) {
        showToast(data.detail || 'Upload failed', 'error');
      } else {
        showToast(`"${file.name}" uploaded — click Process to index it`);
        await fetchDocs();
      }
    } catch (e) {
      showToast('Upload failed. Is the server running?', 'error');
    }
    setUploading(false);
  };

  // ── Process ────────────────────────────────────────────────────────────────
  const handleProcess = async (doc: DocRecord) => {
    setProcessingId(doc.id);
    try {
      const res  = await fetch(`/admin/documents/${doc.id}/process`, {
        method:  'POST',
        headers: adminHeaders(),
      });
      const data = await res.json();

      if (data.status === 'indexed') {
        showToast(`Indexed ${data.chunk_count} chunks from ${data.page_count} pages`);
      } else if (data.status === 'failed') {
        showToast(data.error_message || 'Processing failed', 'error');
      }
      await fetchDocs();
    } catch (_) {
      showToast('Processing failed', 'error');
    }
    setProcessingId(null);
  };

  // ── Delete ─────────────────────────────────────────────────────────────────
  const handleDelete = async (doc: DocRecord) => {
    if (!window.confirm(`Delete "${doc.original_name}"? This cannot be undone.`)) return;
    try {
      await fetch(`/admin/documents/${doc.id}`, {
        method:  'DELETE',
        headers: adminHeaders(),
      });
      showToast(`"${doc.original_name}" deleted`);
      await fetchDocs();
    } catch (_) {
      showToast('Delete failed', 'error');
    }
  };

  // ── Drag & Drop ────────────────────────────────────────────────────────────
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFileSelect(file);
  };

  // ── Summary stats ──────────────────────────────────────────────────────────
  const totalIndexed = docs.filter(d => d.status === 'indexed').length;
  const totalChunks  = docs.reduce((s, d) => s + (d.chunk_count || 0), 0);
  const totalPages   = docs.reduce((s, d) => s + (d.page_count  || 0), 0);

  // ─────────────────────────────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-gray-900 text-white font-sans">

      {/* Toast */}
      <AnimatePresence>
        {toast && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className={`fixed top-4 right-4 z-50 px-5 py-3 rounded-2xl text-sm font-medium shadow-2xl flex items-center gap-2 ${
              toast.type === 'error'
                ? 'bg-red-900 border border-red-700 text-red-100'
                : 'bg-emerald-900 border border-emerald-700 text-emerald-100'
            }`}
          >
            {toast.type === 'error'
              ? <AlertCircle className="w-4 h-4" />
              : <CheckCircle className="w-4 h-4" />
            }
            {toast.msg}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Chunk preview modal */}
      {previewDoc && <ChunkModal doc={previewDoc} onClose={() => setPreviewDoc(null)} />}

      {/* Nav */}
      <nav className="fixed top-0 w-full z-40 bg-gray-900/80 backdrop-blur-lg border-b border-gray-800">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/admin/dashboard')}
              className="p-2 hover:bg-gray-800 rounded-xl transition-colors"
            >
              <ArrowLeft className="w-5 h-5 text-gray-400" />
            </button>
            <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
              <Database className="w-4 h-4 text-white" />
            </div>
            <span className="font-semibold text-white">Document Manager</span>
          </div>
          <button
            onClick={fetchDocs}
            className="p-2 hover:bg-gray-800 rounded-xl transition-colors"
          >
            <RefreshCw className={`w-4 h-4 text-gray-400 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </nav>

      <main className="pt-24 pb-16 px-6 max-w-6xl mx-auto">

        {/* Tab switcher */}
        <div className="flex gap-1 mb-8 bg-gray-800/60 border border-gray-700 rounded-2xl p-1 w-fit">
          {[
            { id: 'documents' as const, label: 'Documents',  Icon: Database },
            { id: 'qa'        as const, label: 'Policy Q&A', Icon: MessageSquare },
          ].map(({ id, label, Icon }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id)}
              className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium transition-all ${
                activeTab === id
                  ? 'bg-indigo-600 text-white shadow-lg'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              <Icon className="w-4 h-4" />
              {label}
            </button>
          ))}
        </div>

        {activeTab === 'qa' && <PolicyQA />}

        {activeTab === 'documents' && (<>

        {/* Summary cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {[
            { label: 'Total Docs',    value: docs.length,    icon: FileText,   color: 'text-indigo-400' },
            { label: 'Indexed',       value: totalIndexed,   icon: CheckCircle,color: 'text-emerald-400' },
            { label: 'Total Chunks',  value: totalChunks,    icon: Hash,       color: 'text-purple-400' },
            { label: 'Total Pages',   value: totalPages,     icon: HardDrive,  color: 'text-cyan-400' },
          ].map(({ label, value, icon: Icon, color }) => (
            <div key={label} className="bg-gray-800 border border-gray-700 rounded-2xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <Icon className={`w-4 h-4 ${color}`} />
                <span className="text-xs text-gray-400">{label}</span>
              </div>
              <p className="text-2xl font-bold text-white">{value}</p>
            </div>
          ))}
        </div>

        {/* Upload zone */}
        <div
          onDragOver={e => { e.preventDefault(); setIsDragOver(true); }}
          onDragLeave={() => setIsDragOver(false)}
          onDrop={handleDrop}
          className={`mb-8 border-2 border-dashed rounded-3xl p-10 text-center transition-all cursor-pointer ${
            isDragOver
              ? 'border-indigo-400 bg-indigo-900/20'
              : 'border-gray-700 bg-gray-800/40 hover:border-gray-500 hover:bg-gray-800/60'
          }`}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            className="hidden"
            onChange={e => { const f = e.target.files?.[0]; if (f) handleFileSelect(f); e.target.value = ''; }}
          />
          {uploading ? (
            <div className="flex flex-col items-center gap-3">
              <Loader className="w-10 h-10 text-indigo-400 animate-spin" />
              <p className="text-gray-300 font-medium">Uploading…</p>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-3">
              <Upload className={`w-10 h-10 ${isDragOver ? 'text-indigo-400' : 'text-gray-500'}`} />
              <div>
                <p className="text-white font-semibold">Drop a PDF here or click to upload</p>
                <p className="text-gray-500 text-sm mt-1">PDF only · Max 50 MB</p>
              </div>
            </div>
          )}
        </div>

        {/* Documents table */}
        <div className="bg-gray-800 border border-gray-700 rounded-3xl overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-700 flex items-center justify-between">
            <h2 className="font-semibold text-white flex items-center gap-2">
              <FileText className="w-4 h-4 text-indigo-400" />
              Uploaded Documents
              <span className="text-gray-500 font-normal text-sm">({docs.length})</span>
            </h2>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-16">
              <Loader className="w-6 h-6 text-indigo-400 animate-spin" />
            </div>
          ) : docs.length === 0 ? (
            <div className="text-center py-16 text-gray-500">
              <FileText className="w-12 h-12 mx-auto mb-3 opacity-30" />
              <p>No documents uploaded yet.</p>
              <p className="text-sm mt-1">Upload a PDF above to get started.</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-700/50">
              {docs.map(doc => (
                <motion.div
                  key={doc.id}
                  layout
                  className="px-6 py-4 flex items-center gap-4 hover:bg-gray-700/30 transition-colors"
                >
                  {/* File icon */}
                  <div className="w-10 h-10 bg-gray-700 rounded-xl flex items-center justify-center flex-shrink-0">
                    <FileText className="w-5 h-5 text-indigo-400" />
                  </div>

                  {/* Info */}
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-white truncate">{doc.original_name}</p>
                    <div className="flex items-center gap-3 mt-1 text-xs text-gray-500">
                      <span>{fmtBytes(doc.file_size)}</span>
                      {doc.page_count  && <span>· {doc.page_count} pages</span>}
                      {doc.chunk_count && <span>· {doc.chunk_count} chunks</span>}
                      <span>· {fmtDate(doc.uploaded_at)}</span>
                    </div>
                    {doc.error_message && (
                      <p className="text-xs text-red-400 mt-1 truncate">{doc.error_message}</p>
                    )}
                  </div>

                  {/* Status */}
                  <div className="flex-shrink-0">
                    <StatusBadge status={doc.status} />
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2 flex-shrink-0">
                    {/* Process / Reprocess */}
                    {(doc.status === 'pending' || doc.status === 'failed') && (
                      <button
                        onClick={() => handleProcess(doc)}
                        disabled={processingId === doc.id}
                        className="flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-xl bg-indigo-900/60 hover:bg-indigo-900/80 text-indigo-300 border border-indigo-700/50 transition-colors disabled:opacity-50"
                      >
                        {processingId === doc.id
                          ? <Loader className="w-3 h-3 animate-spin" />
                          : <RefreshCw className="w-3 h-3" />
                        }
                        Process
                      </button>
                    )}
                    {doc.status === 'indexed' && (
                      <>
                        <button
                          onClick={() => setPreviewDoc(doc)}
                          className="flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-xl bg-purple-900/60 hover:bg-purple-900/80 text-purple-300 border border-purple-700/50 transition-colors"
                        >
                          <ChevronRight className="w-3 h-3" />
                          Chunks
                        </button>
                        <button
                          onClick={() => handleProcess(doc)}
                          disabled={processingId === doc.id}
                          className="flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-xl bg-gray-700 hover:bg-gray-600 text-gray-300 transition-colors disabled:opacity-50"
                        >
                          <RefreshCw className="w-3 h-3" />
                          Re-index
                        </button>
                      </>
                    )}

                    {/* Delete */}
                    <button
                      onClick={() => handleDelete(doc)}
                      className="p-1.5 rounded-xl hover:bg-red-900/40 text-gray-500 hover:text-red-400 transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>

        {/* Demo note */}
        <div className="mt-6 bg-amber-900/20 border border-amber-700/40 rounded-2xl p-4 text-sm text-amber-300 flex items-start gap-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
          <span>
            <strong>Admin only.</strong> Customers cannot view or modify policy documents.
            Only upload official, authorised documents. A demo PDF (clearly marked as non-official) is available for testing.
          </span>
        </div>

        </>)}

      </main>
    </div>
  );
};
