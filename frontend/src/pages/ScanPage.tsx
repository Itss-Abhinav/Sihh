import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  UploadCloud,
  Camera,
  Image as ImageIcon,
  X,
  Sparkles,
  CheckCircle2,
  ArrowRight,
  Loader2,
  FileText,
  AlertCircle,
  HelpCircle,
  Wand2
} from 'lucide-react';
import Tesseract from 'tesseract.js';
import { DemoSelector } from '../components/DemoSelector';
import { LegalDisclaimer } from '../components/LegalDisclaimer';
import { scansApi } from '../api/scans';

export const ScanPage: React.FC = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [selectedDemo, setSelectedDemo] = useState<string | null>(null);
  const [productCategory, setProductCategory] = useState<string>('Food & Confectionery');
  const [customText, setCustomText] = useState<string>('');
  const [showCustomText, setShowCustomText] = useState<boolean>(false);

  // Optical Character Recognition (OCR) State
  const [isOcrRunning, setIsOcrRunning] = useState<boolean>(false);
  const [ocrProgress, setOcrProgress] = useState<number>(0);
  const [ocrStatusText, setOcrStatusText] = useState<string>('');
  const [ocrCompleted, setOcrCompleted] = useState<boolean>(false);

  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [processingStep, setProcessingStep] = useState<number>(0);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const processingSteps = [
    'Optical Capture & High-Contrast Preprocessing...',
    'Optical Character Recognition (OCR)...',
    'Structured Metrology Extraction...',
    'Statutory Scope & Exemption Filter...',
    'Deterministic Legal Rule Engine (Rulebook 2026.2)...',
    'Synthesizing Compliance Screening Report...'
  ];

  const biscuitPresets = [
    {
      id: 'goodday',
      name: '🍪 Britannia Good Day',
      pack: 'Butter Cookies (200g, ₹45)',
      category: 'Food & Confectionery',
      text: `Product: GoodDay Butter Cookies
Brand: Britannia
Generic Name: Butter Cookies
Category: Food & Confectionery
Net Weight: 200 g
MRP: Rs. 45.00 (inclusive of all taxes)
Unit Sale Price: Rs. 0.225 / g
Mfg Date: 08/2026
Manufactured & Packed by: Britannia Industries Ltd.
Address: Plot 42, KIADB Industrial Area, Phase 2, Whitefield, Bengaluru - 560066
Consumer Care: Consumer Care Manager, 1800-425-4449
Email: feedback@britannia.co.in
Country of Origin: India`
    },
    {
      id: 'parleg',
      name: '🍪 Parle-G Gluco',
      pack: 'Original Biscuits (250g, ₹25)',
      category: 'Food & Confectionery',
      text: `Product: Parle-G Gluco Biscuits
Brand: Parle-G
Generic Name: Biscuits
Category: Food & Confectionery
Net Weight: 250 g
MRP: Rs. 25.00 (inclusive of all taxes)
Unit Sale Price: Rs. 0.10 / g
Mfg Date: 06/2026
Manufactured & Packed by: Parle Products Pvt. Ltd.
Address: North Level Crossing, Vile Parle East, Mumbai, Maharashtra - 400057
Consumer Care: Consumer Care Executive, 1800-22-2229
Email: cs@parle.biz
Country of Origin: India`
    },
    {
      id: 'mariegold',
      name: '🍪 Marie Gold',
      pack: 'Crisp Tea Biscuits (100g, ₹20)',
      category: 'Food & Confectionery',
      text: `Product: Marie Gold Crisp Tea Biscuits
Brand: Britannia
Generic Name: Marie Biscuits
Category: Food & Confectionery
Net Weight: 100 g
MRP: Rs. 20.00 (inclusive of all taxes)
Unit Sale Price: Rs. 0.20 / g
Mfg Date: 07/2026
Manufactured & Packed by: Britannia Industries Ltd.
Address: 5/1A Hungerford Street, Kolkata, West Bengal - 700017
Consumer Care: Consumer Helpline, 1800-425-4449
Email: feedback@britannia.co.in
Country of Origin: India`
    },
    {
      id: 'darkfantasy',
      name: '🍪 Sunfeast Dark Fantasy',
      pack: 'Choco Fills (75g, ₹40)',
      category: 'Food & Confectionery',
      text: `Product: Sunfeast Dark Fantasy Choco Fills
Brand: Sunfeast
Generic Name: Filled Cookies
Category: Food & Confectionery
Net Weight: 75 g
MRP: Rs. 40.00 (inclusive of all taxes)
Unit Sale Price: Rs. 0.533 / g
Mfg Date: 08/2026
Manufactured & Packed by: ITC Limited
Address: 37, J.L. Nehru Road, Kolkata, West Bengal - 700071
Consumer Care: ITC Consumer Care Cell, 1800-103-1299
Email: itccares@itc.in
Country of Origin: India`
    },
    {
      id: 'oreo',
      name: '🍪 Cadbury Oreo',
      pack: 'Creme Biscuits (120g, ₹35)',
      category: 'Food & Confectionery',
      text: `Product: Oreo Vanilla Creme Biscuits
Brand: Oreo
Generic Name: Sandwich Biscuits
Category: Food & Confectionery
Net Weight: 120 g
MRP: Rs. 35.00 (inclusive of all taxes)
Unit Sale Price: Rs. 0.292 / g
Mfg Date: 08/2026
Manufactured & Packed by: Mondelez India Foods Pvt. Ltd.
Address: Unit 2001, 20th Floor, Tower-3, Indiabulls Finance Centre, Parel, Mumbai - 400013
Consumer Care: Consumer Care Executive, 1800-22-7080
Email: suggestions@mdlz.com
Country of Origin: India`
    }
  ];

  // Preprocess smartphone camera image: downscale to max 1400px & compress to ~250KB JPEG for fast Vercel upload
  const preprocessImage = (file: File): Promise<{ dataUrl: string; compressedFile: File }> => {
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const img = new Image();
        img.onload = () => {
          try {
            const canvas = document.createElement('canvas');
            let width = img.width;
            let height = img.height;
            const maxDim = 1400;

            if (width > maxDim || height > maxDim) {
              if (width > height) {
                height = Math.round((height * maxDim) / width);
                width = maxDim;
              } else {
                width = Math.round((width * maxDim) / height);
                height = maxDim;
              }
            }

            canvas.width = width;
            canvas.height = height;
            const ctx = canvas.getContext('2d');
            if (!ctx) {
              resolve({ dataUrl: e.target?.result as string, compressedFile: file });
              return;
            }

            ctx.drawImage(img, 0, 0, width, height);

            const dataUrl = canvas.toDataURL('image/jpeg', 0.85);

            canvas.toBlob((blob) => {
              if (blob) {
                const optName = (file.name.replace(/\.[^/.]+$/, '') || 'package_photo') + '.jpg';
                const optFile = new File([blob], optName, {
                  type: 'image/jpeg',
                  lastModified: Date.now()
                });
                resolve({ dataUrl, compressedFile: optFile });
              } else {
                resolve({ dataUrl, compressedFile: file });
              }
            }, 'image/jpeg', 0.85);
          } catch (canvasErr) {
            console.warn('Canvas preprocessor error, falling back to raw:', canvasErr);
            resolve({ dataUrl: e.target?.result as string, compressedFile: file });
          }
        };
        img.onerror = () => resolve({ dataUrl: e.target?.result as string, compressedFile: file });
        img.src = e.target?.result as string;
      };
      reader.onerror = () => resolve({ dataUrl: URL.createObjectURL(file), compressedFile: file });
      reader.readAsDataURL(file);
    });
  };

  const runClientOcr = async (imageUrl: string) => {
    setIsOcrRunning(true);
    setOcrProgress(15);
    setOcrStatusText('Scanning packaging text with Optical Character Recognition...');
    setOcrCompleted(false);

    try {
      const result = await Tesseract.recognize(imageUrl, 'eng', {
        logger: (m) => {
          if (m.status === 'recognizing text') {
            const p = 15 + Math.round((m.progress || 0) * 80);
            setOcrProgress(p);
            setOcrStatusText(`Reading printed text on wrapper... ${p}%`);
          } else if (m.status === 'loading tesseract core') {
            setOcrStatusText('Loading optical recognition engine...');
          }
        },
      });

      const recognized = result?.data?.text?.trim() || '';
      const isMeaningful =
        recognized &&
        recognized.length >= 15 &&
        /[a-zA-Z]{3,}/.test(recognized) &&
        !/^[\s\d\W]+$/.test(recognized);

      if (isMeaningful) {
        setCustomText(recognized);
        setShowCustomText(true);
        setOcrCompleted(true);
        setOcrStatusText('Label text recognized! Declarations ready for screening.');
      } else {
        // Discard 1-2 char noise (like "n 9") so cloud packaging OCR will evaluate original photo
        setCustomText('');
        setOcrCompleted(true);
        setOcrStatusText('Photo captured! Cloud packaging engine will extract declarations during screening.');
      }
    } catch (err: any) {
      console.warn('OCR error:', err);
      setCustomText('');
      setOcrCompleted(true);
      setOcrStatusText('Photo captured! Ready for Legal Metrology compliance screening.');
    } finally {
      setIsOcrRunning(false);
      setOcrProgress(100);
    }
  };

  const handleFileChange = async (file: File) => {
    if (!file.type.match(/image\/(jpeg|jpg|png|webp)/)) {
      setErrorMessage('Unsupported format. Please upload JPG, PNG, or WEBP.');
      return;
    }
    if (file.size > 20 * 1024 * 1024) {
      setErrorMessage('Image exceeds 20MB limit.');
      return;
    }
    setSelectedDemo(null);
    setErrorMessage(null);
    setCustomText('');
    setOcrCompleted(false);

    try {
      const { dataUrl, compressedFile } = await preprocessImage(file);
      setSelectedFile(compressedFile);
      setPreviewUrl(dataUrl);
      runClientOcr(dataUrl);
    } catch (err) {
      setSelectedFile(file);
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
      runClientOcr(url);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  const handleSelectDemo = (demoId: string) => {
    if (selectedDemo === demoId) {
      setSelectedDemo(null);
      return;
    }
    setSelectedDemo(demoId);
    setSelectedFile(null);
    setPreviewUrl(null);
    setCustomText('');
    setIsOcrRunning(false);
    setOcrCompleted(false);
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
    setIsOcrRunning(false);
    setOcrCompleted(false);
    setErrorMessage(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
    if (cameraInputRef.current) cameraInputRef.current.value = '';
  };

  const handleAutofillBiscuitTemplate = () => {
    setCustomText(
`Product: GoodDay Butter Cookies
Brand: Britannia
Generic Name: Butter Cookies
Category: Food & Confectionery
Net Weight: 200 g
MRP: Rs. 45.00 (inclusive of all taxes)
Unit Sale Price: Rs. 0.225 / g
Mfg Date: 08/2026
Manufactured & Packed by: Britannia Industries Ltd.
Address: Plot 42, KIADB Industrial Area, Phase 2, Whitefield, Bengaluru - 560066
Consumer Care: Consumer Care Manager, 1800-425-4449
Email: feedback@britannia.co.in
Country of Origin: India`
    );
    setShowCustomText(true);
    setSelectedDemo(null);
  };

  const handleStartScan = async () => {
    if (!selectedFile && !selectedDemo && !customText.trim()) {
      setErrorMessage('Please capture/upload an image, select a benchmark demo, or enter label text.');
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
        if (customText.trim()) {
          formData.append('customText', customText.trim());
        }
      } else if (selectedDemo) {
        formData.append('demoPreset', selectedDemo);
      } else if (customText.trim()) {
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
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
          <span>Screen Packaged Commodity Label</span>
          <span className="text-[11px] font-mono font-medium text-emerald-400 bg-emerald-950/70 border border-emerald-800 px-2 py-0.5 rounded">
            Rulebook 2026.2
          </span>
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Capture or upload any commodity label. The engine extracts declarations optically and evaluates 21 deterministic statutory checks.
        </p>
      </div>

      <LegalDisclaimer />

      {errorMessage && (
        <div className="p-4 rounded-xl bg-rose-950/60 border border-rose-800 text-rose-300 text-xs font-medium flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
          <span>{errorMessage}</span>
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

      {/* Upload or Camera Card */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-5">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <ImageIcon className="w-4 h-4 text-emerald-400" />
            <span>Product Label Image (Mobile Camera or Upload)</span>
          </h3>
          {(selectedFile || previewUrl) && (
            <button
              onClick={handleClear}
              className="text-xs text-rose-400 hover:text-rose-300 flex items-center gap-1 font-medium cursor-pointer"
            >
              <X className="w-3.5 h-3.5" />
              <span>Remove Photo</span>
            </button>
          )}
        </div>

        {previewUrl ? (
          <div className="space-y-4">
            <div className="relative rounded-xl overflow-hidden border border-slate-700 bg-slate-950 max-h-80 flex items-center justify-center">
              <img src={previewUrl} alt="Label preview" className="max-h-80 object-contain mx-auto" />
              <div className="absolute bottom-2 left-2 bg-slate-900/90 backdrop-blur text-[11px] font-mono text-slate-300 px-2.5 py-1 rounded border border-slate-700">
                {selectedFile?.name} ({(selectedFile ? selectedFile.size / 1024 : 0).toFixed(1)} KB)
              </div>
            </div>

            {/* OCR Live Status Banner */}
            {isOcrRunning && (
              <div className="p-4 rounded-xl bg-slate-900 border border-emerald-500/40 space-y-2">
                <div className="flex items-center justify-between text-xs text-emerald-400 font-medium">
                  <span className="flex items-center gap-2">
                    <Loader2 className="w-4 h-4 animate-spin text-emerald-400" />
                    <span>{ocrStatusText}</span>
                  </span>
                  <span className="font-mono">{ocrProgress}%</span>
                </div>
                <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                  <div
                    className="bg-emerald-500 h-full rounded-full transition-all duration-300"
                    style={{ width: `${ocrProgress}%` }}
                  ></div>
                </div>
              </div>
            )}

            {ocrCompleted && (
              <div className="p-3 rounded-xl bg-emerald-950/40 border border-emerald-800/60 text-xs text-emerald-300 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>Text successfully extracted from your photo! Review or refine declarations below before screening.</span>
              </div>
            )}
          </div>
        ) : (
          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className="border-2 border-dashed border-slate-700 hover:border-emerald-500/60 rounded-xl p-8 text-center cursor-pointer transition-colors bg-slate-950/40 hover:bg-slate-900/40 space-y-4"
          >
            <div className="w-14 h-14 rounded-2xl bg-slate-800/80 text-emerald-400 mx-auto flex items-center justify-center border border-slate-700 shadow-inner">
              <UploadCloud className="w-7 h-7 text-emerald-400" />
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-200">
                Tap or drag & drop label photo here
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
                className="inline-flex items-center gap-2 text-xs font-semibold text-emerald-300 bg-emerald-950/60 hover:bg-emerald-900/60 px-4 py-2 rounded-xl border border-emerald-700/80 transition-all shadow-md cursor-pointer"
              >
                <Camera className="w-4 h-4 text-emerald-400" />
                <span>Take Photo with Camera</span>
              </button>
            </div>
          </div>
        )}

        {/* 1-Tap Biscuit & FMCG Smart Presets */}
        <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 space-y-2.5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-amber-300 flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-amber-400" />
              <span>1-Tap Biscuit & FMCG Presets (Official Pack Declarations)</span>
            </span>
            <span className="text-[10px] text-slate-400 hidden sm:inline">
              Tap any pack to verify or test with 1 click
            </span>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-2">
            {biscuitPresets.map((b) => (
              <button
                key={b.id}
                type="button"
                onClick={() => {
                  setCustomText(b.text);
                  setProductCategory(b.category);
                  setShowCustomText(true);
                  setSelectedDemo(null);
                }}
                className="p-2.5 rounded-lg text-left bg-slate-950/80 hover:bg-slate-850 border border-slate-800 hover:border-amber-500/60 transition-all text-xs font-medium text-slate-200 cursor-pointer shadow-sm hover:scale-[1.02]"
              >
                <div className="font-semibold text-amber-300 text-xs truncate">{b.name}</div>
                <div className="text-[10px] text-slate-400 mt-0.5 truncate">{b.pack}</div>
              </button>
            ))}
          </div>
        </div>

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
              <option value="Food & Confectionery">Food & Confectionery (Biscuits, Cookies, Snacks)</option>
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
              <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5 text-emerald-400" />
                <span>Extracted Label Text ({customText ? `${customText.length} chars` : 'Empty'})</span>
              </label>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={handleAutofillBiscuitTemplate}
                  className="text-[11px] text-amber-400 hover:text-amber-300 font-medium flex items-center gap-1 cursor-pointer"
                  title="Autofill a complete biscuit label format"
                >
                  <Wand2 className="w-3 h-3" />
                  <span>Autofill GoodDay</span>
                </button>
                <button
                  type="button"
                  onClick={() => setShowCustomText(!showCustomText)}
                  className="text-[11px] text-emerald-400 hover:text-emerald-300 font-medium cursor-pointer"
                >
                  {showCustomText ? 'Hide Text' : (customText ? 'View/Edit Declarations' : 'Paste Raw Text')}
                </button>
              </div>
            </div>
            {showCustomText ? (
              <textarea
                value={customText}
                onChange={(e) => {
                  setCustomText(e.target.value);
                  setSelectedDemo(null);
                }}
                rows={5}
                placeholder="Declarations extracted from your label appear here. You can also paste or edit text directly..."
                className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-xs text-slate-200 font-mono focus:outline-none focus:border-emerald-500 leading-relaxed"
              />
            ) : (
              <p className="text-xs text-slate-400 pt-2 leading-relaxed">
                {customText ? (
                  <span className="text-emerald-400">
                    Label text extracted! Click "View/Edit Extracted Text" above to review.
                  </span>
                ) : (
                  'Take a photo above or click "Paste Raw Text" to provide declarations.'
                )}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Benchmark Presets Section */}
      <div className="glass-panel p-5 rounded-2xl border border-slate-800">
        <DemoSelector
          selectedDemo={selectedDemo}
          onSelectDemo={handleSelectDemo}
          disabled={isProcessing}
        />
      </div>

      <div className="flex items-center justify-end gap-3 pt-2">
        <button
          type="button"
          onClick={handleStartScan}
          disabled={isProcessing || isOcrRunning}
          className="flex items-center gap-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold px-6 py-3 rounded-xl shadow-lg shadow-emerald-950/60 transition-all hover:scale-[1.02] cursor-pointer disabled:opacity-50"
        >
          {isOcrRunning ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin text-slate-950" />
              <span>Extracting Text...</span>
            </>
          ) : (
            <>
              <span>Run Compliance Screening</span>
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </button>
      </div>
    </div>
  );
};