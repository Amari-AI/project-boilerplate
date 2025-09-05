"use client";

import { useEffect, useMemo, useState } from "react";

type ExtractedFields = {
  billOfLadingNumber: string;
  containerNumber: string;
  consigneeName: string;
  consigneeAddress: string;
  date: string;
  lineItemsCount: string;
  averageGrossWeight: string;
  averagePrice: string;
};

const DEFAULT_FIELDS: ExtractedFields = {
  billOfLadingNumber: "",
  containerNumber: "",
  consigneeName: "",
  consigneeAddress: "",
  date: "",
  lineItemsCount: "",
  averageGrossWeight: "",
  averagePrice: "",
};

function tryParseJSON(text: any): any | null {
  if (typeof text !== "string") return text;
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}

function coerceToFields(data: any): ExtractedFields {
  // Accepts either an object with known keys or a raw string and tries to extract values
  if (data && typeof data === "object") {
    const d = data as Record<string, any>;
    const get = (...keys: string[]) => keys.map((k) => d[k])
      .find((v) => typeof v === "string" || typeof v === "number") ?? "";
    return {
      billOfLadingNumber: String(
        get("bill_of_lading_number", "billOfLadingNumber", "bol", "bol_number")
      ),
      containerNumber: String(get("container_number", "containerNumber")),
      consigneeName: String(get("consignee_name", "consigneeName")),
      consigneeAddress: String(get("consignee_address", "consigneeAddress")),
      date: String(get("date", "shipment_date")),
      lineItemsCount: String(get("line_items_count", "lineItemsCount")),
      averageGrossWeight: String(get("average_gross_weight", "avgGrossWeight")),
      averagePrice: String(get("average_price", "avgPrice")),
    };
  }

  const text = typeof data === "string" ? data : "";
  const grab = (re: RegExp) => {
    const m = text.match(re);
    return m ? m[1].trim() : "";
  };

  return {
    billOfLadingNumber: grab(/bill\s*of\s*lad(?:ing)?\s*number\s*[:\-]?\s*(.+)/i),
    containerNumber: grab(/container\s*number\s*[:\-]?\s*(.+)/i),
    consigneeName: grab(/consignee\s*name\s*[:\-]?\s*(.+)/i),
    consigneeAddress: grab(/consignee\s*address\s*[:\-]?\s*(.+)/i),
    date: grab(/\bdate\b\s*[:\-]?\s*(.+)/i),
    lineItemsCount: grab(/line\s*items?\s*count\s*[:\-]?\s*(\d+)/i),
    averageGrossWeight: grab(/average\s*gross\s*weight\s*[:\-]?\s*([\d.,]+)/i),
    averagePrice: grab(/average\s*price\s*[:\-]?\s*([\d.,]+)/i),
  };
}

export default function Home() {
  const [files, setFiles] = useState<File[]>([]);
  const [previews, setPreviews] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [rawResult, setRawResult] = useState<any>(null);
  const [fields, setFields] = useState<ExtractedFields>(DEFAULT_FIELDS);

  // Build object URLs for previews
  useEffect(() => {
    const urls: Record<string, string> = {};
    files.forEach((f) => {
      urls[f.name] = URL.createObjectURL(f);
    });
    setPreviews((prev) => {
      // Revoke old URLs not in new files
      Object.entries(prev).forEach(([name, url]) => {
        if (!files.find((f) => f.name === name)) URL.revokeObjectURL(url);
      });
      return urls;
    });
    return () => {
      Object.values(urls).forEach((u) => URL.revokeObjectURL(u));
    };
  }, [files]);

  const apiBase = useMemo(
    () => process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
    []
  );

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;
    setFiles(Array.from(e.target.files));
    setError(null);
    setRawResult(null);
    setFields(DEFAULT_FIELDS);
  };

  const extractData = async () => {
    if (!files.length) return;
    setLoading(true);
    setError(null);
    setRawResult(null);
    try {
      const fd = new FormData();
      for (const f of files) fd.append("files", f, f.name);
      const res = await fetch(`${apiBase}/process-documents`, {
        method: "POST",
        body: fd,
      });
      if (!res.ok) throw new Error(`API error ${res.status}`);
      const json = await res.json();
      const extracted = json?.extracted_data ?? json; // be lenient
      const parsed = tryParseJSON(extracted) ?? extracted;
      setRawResult(parsed);
      setFields(coerceToFields(parsed));
    } catch (err: any) {
      setError(err?.message || "Failed to extract data");
    } finally {
      setLoading(false);
    }
  };

  const updateField = (k: keyof ExtractedFields, v: string) =>
    setFields((prev) => ({ ...prev, [k]: v }));

  const resetAll = () => {
    setFiles([]);
    setPreviews({});
    setFields(DEFAULT_FIELDS);
    setRawResult(null);
    setError(null);
  };

  const showResults = files.length > 0 && (loading || rawResult !== null);

  return (
    <div className="min-h-screen p-6 sm:p-10">
      <header className="mb-6">
        <h1 className="text-2xl font-semibold">Shipment Data Extraction</h1>
        <p className="text-sm opacity-75">Upload shipment docs and extract key fields</p>
      </header>

      <section className="mb-6 rounded-lg border border-white/15 p-4 bg-white/5">
        <div className="flex flex-col sm:flex-row sm:items-end gap-4">
          <div className="flex-1">
            <label className="block text-sm font-medium mb-1">Documents</label>
            <input
              type="file"
              multiple
              accept=".pdf,.xlsx,.xls"
              onChange={handleFileChange}
              className="block w-full text-sm file:mr-3 file:px-3 file:py-1.5 file:rounded-md file:border file:border-white/20 file:bg-white/10 file:text-foreground"
            />
            {files.length > 0 && (
              <ul className="mt-2 text-sm opacity-80 list-disc list-inside">
                {files.map((f) => (
                  <li key={f.name} className="truncate">{f.name}</li>
                ))}
              </ul>
            )}
          </div>
          <div className="flex gap-3">
            <button
              onClick={extractData}
              disabled={!files.length || loading}
              className="px-4 py-2 rounded-md bg-foreground text-background disabled:opacity-40"
            >
              {loading ? "Extracting…" : "Extract Data"}
            </button>
            <button
              onClick={resetAll}
              disabled={!files.length && !rawResult}
              className="px-4 py-2 rounded-md border border-white/20"
            >
              Reset
            </button>
          </div>
        </div>
        {error && (
          <p className="mt-3 text-sm text-red-500">{error}</p>
        )}
      </section>

      <section className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
        <div className="rounded-lg border border-white/15 p-4 bg-white/5">
          <h2 className="text-lg font-medium mb-4">Extracted Fields</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Field
              label="Bill of Lading Number"
              value={fields.billOfLadingNumber}
              onChange={(v) => updateField("billOfLadingNumber", v)}
            />
            <Field
              label="Container Number"
              value={fields.containerNumber}
              onChange={(v) => updateField("containerNumber", v)}
            />
            <Field
              label="Consignee Name"
              value={fields.consigneeName}
              onChange={(v) => updateField("consigneeName", v)}
            />
            <Field
              label="Consignee Address"
              value={fields.consigneeAddress}
              onChange={(v) => updateField("consigneeAddress", v)}
            />
            <Field
              label="Date"
              value={fields.date}
              onChange={(v) => updateField("date", v)}
            />
            <Field
              label="Line Items Count"
              value={fields.lineItemsCount}
              onChange={(v) => updateField("lineItemsCount", v)}
            />
            <Field
              label="Average Gross Weight"
              value={fields.averageGrossWeight}
              onChange={(v) => updateField("averageGrossWeight", v)}
            />
            <Field
              label="Average Price"
              value={fields.averagePrice}
              onChange={(v) => updateField("averagePrice", v)}
            />
          </div>
          {showResults && (
            <details className="mt-4">
              <summary className="cursor-pointer text-sm opacity-80">Show raw extraction</summary>
              <pre className="mt-2 text-xs whitespace-pre-wrap break-words p-2 rounded bg-black/20 border border-white/10">
                {typeof rawResult === "string"
                  ? rawResult
                  : JSON.stringify(rawResult, null, 2)}
              </pre>
            </details>
          )}
        </div>

        <div className="rounded-lg border border-white/15 p-4 bg-white/5">
          <h2 className="text-lg font-medium mb-4">Document Viewer</h2>
          {files.length === 0 ? (
            <p className="text-sm opacity-70">No documents selected.</p>
          ) : (
            <div className="space-y-4">
              {files.map((f) => (
                <div key={f.name} className="border border-white/10 rounded">
                  <div className="flex items-center justify-between px-3 py-2 text-sm border-b border-white/10">
                    <span className="truncate">{f.name}</span>
                    <a
                      className="underline opacity-80 hover:opacity-100"
                      href={previews[f.name]}
                      target="_blank"
                      rel="noreferrer"
                    >
                      Open
                    </a>
                  </div>
                  {f.type === "application/pdf" || f.name.toLowerCase().endsWith(".pdf") ? (
                    <iframe
                      src={previews[f.name]}
                      className="w-full h-[420px]"
                      title={f.name}
                    />
                  ) : (
                    <div className="p-4 text-sm opacity-75">
                      Preview not supported. Use Open to view or download.
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </section>
    </div>
  );
}

function Field({
  label,
  value,
  onChange,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
}) {
  const id = label.toLowerCase().replace(/\s+/g, "-");
  return (
    <label htmlFor={id} className="grid gap-1 text-sm">
      <span className="opacity-80">{label}</span>
      <input
        id={id}
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="px-3 py-2 rounded-md border border-white/20 bg-transparent focus:outline-none focus:ring-2 focus:ring-white/30"
      />
    </label>
  );
}
