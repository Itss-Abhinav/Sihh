import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { UploadCloud, Camera, Image as ImageIcon, X, Sparkles, CheckCircle2, ArrowRight, Loader2 } from 'lucide-react';
import { DemoSelector } from '../components/DemoSelector';
import { LegalDisclaimer } from '../components/LegalDisclaimer';
import { scansApi } from '../api/scans';

export const ScanPage: React.FC = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [selectedDemo, setSelectedDemo] = useState<string | null>('demoA');
  const [productCategory, setProductCategory] = useState<string>('Food & Confectionery');
  const [customText, setCustomText] = useState<string>('');
  const [showCustomText, setShowCustomText] = useState<boolean>(false);

  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [processingStep, setProcessingStep] = useState<number>(0);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const processingSteps = [
    'Optical Capture & Preprocessing...',
    'Optical Character Recognition (OCR)...',
    'Structured Metrology Extraction...',
    'Statutory Scope & Exemption Filter...',
    'Deterministic Legal Rule Engine (Rulebook 2026.2)...',
    'Synthesizing Compliance Screening Report...'
  ];

  const handleFileChange = (file: File) => {
    if (!file.type.match(/image\/(jpeg|jpg|png|webp)/)) {
      setErrorMessage('Unsupported format. Please upload JPG, PNG, or WEBP.');
      return;
    }
    if (file.size > 15 * 1024 * 1024) {
      setErrorMessage('Image exceeds 15MB limit.');
      return;
    }
    setSelectedFile(file);
    setSelectedDemo(null);
    setErrorMessage(null);
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  const handleSelectDemo = (demoId: string) => {
    setSelectedDemo(demoId);
    setSelectedFile(null);
    setPreviewUrl(null);
    setErrorMessage(null);
    if (demoId === 'demoA') setProductCategory('Food & Confectionery');
    if (demoId === 'demoB') setProductCategory('Snack Foods');
    if (demoId === 'demoC') setProductCategory('Personal Care');
  };

  const handleClear = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setSelectedDemo(null);
    setCustomText('');
    setErrorMessage(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
    if (cameraInputRef.current) cameraInputRef.current.value = '';
  };

  const handleStartScan = async () => {
    if (!selectedFile && !selectedDemo && !customText.trim()) {
      setErrorMessage('Please upload an image, choose a benchmark demo, or enter text.');
      return;
    }

    setIsProcessing(true);
    setProcessingStep(0);
    setErrorMessage(null);

    const interval = setInterval(() => {
      setProcessingStep((prev) => (prev < processingSteps.length - 1 ? prev + 1 : prev));
    }, 400);

    try {
      const formData = new FormData();
      if (selectedFile) {
        formData.append('image', selectedFile);
      }
      if (selectedDemo) {
        formData.append('demoPreset', selectedDemo);
      }
      if (customText.trim()) {
        formData.append('customText', customText.trim());
      }
      if (productCategory) {
        formData.append('productCategory', productCategory);
      }

      const res = await scansApi.createScan(formData);
      clearInterval(interval);
      setProcessingStep(processingSteps.length - 1);
      setTimeout(() => {
        navigate(`/report/${res.id}`, { state: { scanResult: res } });
      }, 500);
    } catch (err: any) {
      clearInterval(interval);
      setIsProcessing(false);
      setErrorMessage(err.response?.data?.detail || 'Scan processing failed. Please try again.');
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-8">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">Packaged Commodity Screening Scan</h1>
        <p className="text-xs sm:text-sm text-slate-400 mt-1">
          Upload an image of the retail package label or test with synthetic benchmark presets.
        </p>
      </div>

      <LegalDisclaimer variant="banner" />

      {errorMessage && (
        <div className="p-4 rounded-xl bg-rose-950/60 border border-rose-800 text-rose-300 text-xs font-medium">
          {errorMessage}
        </div>
      )}

      {isProcessing && (
        <div className="fixed inset-0 bg-slate-950/85 backdrop-blur-md z-50 flex items-center justify-center p-4">
          <div className="glass-panel p-8 rounded-2xl max-w-md w-full border border-slate-700 shadow-2xl text-center space-y-6">
            <div className="relative w-16 h-16 mx-auto">
              <div className="absolute inset-0 rounded-full border-4 border-emerald-500/20 animate-ping"></div>
              <div className="w-16 h-16 rounded-full border-4 border-emerald-500 border-t-transparent animate-spin flex items-center justify-center"></div>
              <Sparkles className="w-6 h-6 text-emerald-400 absolute inset-0 m-auto" />
            </div>

            <div>
              <h3 className="text-lg font-bold text-white font-mono">Screening In Progress</h3>
              <p className="text-xs text-emerald-400 mt-1 font-mono">{processingSteps[processingStep]}</p>
            </div>

            <div className="space-y-2 text-left bg-slate-950/60 p-4 rounded-xl border border-slate-800">
              {processingSteps.map((step, idx) => (
                <div key={idx} className="flex items-center gap-2 text-xs">
                  {idx < processingStep ? (
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                  ) : idx === processingStep ? (
                    <Loader2 className="w-3.5 h-3.5 text-emerald-400 animate-spin shrink-0" />
                  ) : (
                    <div className="w-3.5 h-3.5 rounded-full border border-slate-700 shrink-0"></div>
                  )}
                  <span className={idx <= processingStep ? 'text-slate-200 font-medium' : 'text-slate-400'}>
                    {step.replace('...', '')}
                  </span>
                </div>
              ))}
            </div>

            <p className="text-[11px] text-slate-400 italic">
              Automated screening result — not a legal determination.
            </p>
          </div>
        </div>
      )}

      <div className="glass-panel p-5 rounded-2xl border border-slate-800">
        <DemoSelector
          selectedDemo={selectedDemo}
          onSelectDemo={handleSelectDemo}
          disabled={isProcessing}
        />
      </div>

      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-5">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <ImageIcon className="w-4 h-4 text-emerald-400" />
            <span>Upload Label Image (Optional if using Benchmark)</span>
          </h3>
          {(selectedFile || previewUrl) && (
            <button
              onClick={handleClear}
              className="text-xs text-rose-400 hover:text-rose-300 flex items-center gap-1 font-medium"
            >
              <X className="w-3.5 h-3.5" />
              <span>Remove</span>
            </button>
          )}
        </div>

        {previewUrl ? (
          <div className="relative rounded-xl overflow-hidden border border-slate-700 bg-slate-950 max-h-80 flex items-center justify-center">
            <img src={previewUrl} alt="Label preview" className="max-h-80 object-contain mx-auto" />
            <div className="absolute bottom-2 left-2 bg-slate-900/80 backdrop-blur text-[11px] font-mono text-slate-300 px-2 py-1 rounded border border-slate-700">
              {selectedFile?.name} ({(selectedFile ? selectedFile.size / 1024 : 0).toFixed(1)} KB)
            </div>
          </div>
        ) : (
          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className="border-2 border-dashed border-slate-700 hover:border-emerald-500/60 rounded-xl p-8 text-center cursor-pointer transition-colors bg-slate-950/40 hover:bg-slate-900/40 space-y-3"
          >
            <div className="w-12 h-12 rounded-xl bg-slate-800 text-slate-400 mx-auto flex items-center justify-center">
              <UploadCloud className="w-6 h-6 text-emerald-400" />
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-200">
                Drag & drop label image here, or <span className="text-emerald-400 underline">browse files</span>
              </p>
              <p className="text-xs text-slate-400 mt-1">Supports JPG, JPEG, PNG, WEBP (up to 15MB)</p>
            </div>

            <div className="pt-2 flex items-center justify-center gap-3">
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  cameraInputRef.current?.click();
                }}
                className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-200 bg-slate-800 hover:bg-slate-700 px-3 py-1.5 rounded-lg border border-slate-700 transition-colors"
              >
                <Camera className="w-3.5 h-3.5 text-emerald-400" />
                <span>Use Mobile Camera</span>
              </button>
            </div>
          </div>
        )}

        <input
          ref={fileInputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp,image/jpg"
          className="hidden"
          onChange={(e) => e.target.files && e.target.files[0] && handleFileChange(e.target.files[0])}
        />
        <input
          ref={cameraInputRef}
          type="file"
          accept="image/*"
          capture="environment"
          className="hidden"
          onChange={(e) => e.target.files && e.target.files[0] && handleFileChange(e.target.files[0])}
        />

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">Commodity Category</label>
            <select
              value={productCategory}
              onChange={(e) => setProductCategory(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
            >
              <option value="Food & Confectionery">Food & Confectionery (Biscuits, Snacks, Grains)</option>
              <option value="Personal Care">Personal Care (Soaps, Lotions, Wash)</option>
              <option value="Cosmetics">Cosmetics & Toiletries</option>
              <option value="Snack Foods">Snack Foods</option>
              <option value="Beverages">Beverages & Bottled Water</option>
              <option value="Readymade Garments">Readymade Garments & Textiles</option>
              <option value="General Commodity">General Packaged Commodity</option>
            </select>
          </div>

          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-xs font-semibold text-slate-300">Custom OCR / Label Text</label>
              <button
                type="button"
                onClick={() => setShowCustomText(!showCustomText)}
                className="text-[11px] text-emerald-400 hover:text-emerald-300"
              >
                {showCustomText ? 'Collapse Textbox' : 'Paste Raw Text'}
              </button>
            </div>
            {showCustomText ? (
              <textarea
                value={customText}
                onChange={(e) => {
                  setCustomText(e.target.value);
                  setSelectedDemo(null);
                }}
                rows={3}
                placeholder="Paste OCR text here to test rule engine clauses..."
                className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-xs text-slate-200 font-mono focus:outline-none focus:border-emerald-500"
              />
            ) : (
              <p className="text-xs text-slate-400 pt-2 leading-relaxed">
                Click "Paste Raw Text" above to paste test label strings directly.
              </p>
            )}
          </div>
        </div>
      </div>

      <div className="flex items-center justify-end gap-3 pt-2">
        <button
          type="button"
          onClick={handleStartScan}
          disabled={isProcessing}
          className="flex items-center gap-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold px-6 py-3 rounded-xl shadow-lg shadow-emerald-950/60 transition-all hover:scale-[1.02] cursor-pointer disabled:opacity-50"
        >
          <span>Run Compliance Screening</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};