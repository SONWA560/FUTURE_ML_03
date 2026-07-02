"use client";

import { useEffect, useState } from "react";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { listCategories, uploadResume, type UploadedCandidate } from "@/lib/api";

export interface ResumeSetup {
  mode: "sample" | "upload";
  selectedCategories: string[];
  perCategoryLimit: number;
  uploadedCandidates: UploadedCandidate[];
}

interface ResumePickerProps {
  value: ResumeSetup;
  onChange: (value: ResumeSetup) => void;
}

export function ResumePicker({ value, onChange }: ResumePickerProps) {
  const [categories, setCategories] = useState<string[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  useEffect(() => {
    listCategories()
      .then(setCategories)
      .catch((err) => setUploadError(err.message));
  }, []);

  function toggleCategory(category: string) {
    const isSelected = value.selectedCategories.includes(category);
    const selectedCategories = isSelected
      ? value.selectedCategories.filter((c) => c !== category)
      : [...value.selectedCategories, category];
    onChange({ ...value, selectedCategories });
  }

  async function handleFilesSelected(files: FileList | null) {
    if (!files || files.length === 0) return;
    setUploading(true);
    setUploadError(null);
    try {
      const uploaded: UploadedCandidate[] = [];
      for (const file of Array.from(files)) {
        uploaded.push(await uploadResume(file));
      }
      onChange({ ...value, uploadedCandidates: [...value.uploadedCandidates, ...uploaded] });
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  }

  function removeUploaded(id: string) {
    onChange({
      ...value,
      uploadedCandidates: value.uploadedCandidates.filter((c) => c.id !== id),
    });
  }

  return (
    <div className="space-y-4">
      <RadioGroup
        value={value.mode}
        onValueChange={(mode) => onChange({ ...value, mode: mode as "sample" | "upload" })}
        className="flex gap-6"
      >
        <div className="flex items-center gap-2">
          <RadioGroupItem value="sample" id="mode-sample" />
          <Label htmlFor="mode-sample">Use sample resumes</Label>
        </div>
        <div className="flex items-center gap-2">
          <RadioGroupItem value="upload" id="mode-upload" />
          <Label htmlFor="mode-upload">Upload my own</Label>
        </div>
      </RadioGroup>

      {value.mode === "sample" ? (
        <div className="space-y-3">
          <div className="space-y-2">
            <Label>Categories to include</Label>
            <div className="flex flex-wrap gap-2">
              {categories.map((category) => {
                const selected = value.selectedCategories.includes(category);
                return (
                  <Badge
                    key={category}
                    variant={selected ? "default" : "outline"}
                    className="cursor-pointer select-none"
                    onClick={() => toggleCategory(category)}
                  >
                    {category}
                  </Badge>
                );
              })}
            </div>
          </div>
          <div className="space-y-2 max-w-40">
            <Label htmlFor="per-category-limit">Resumes per category</Label>
            <Input
              id="per-category-limit"
              type="number"
              min={1}
              max={30}
              value={value.perCategoryLimit}
              onChange={(e) =>
                onChange({ ...value, perCategoryLimit: Number(e.target.value) || 1 })
              }
            />
          </div>
          <p className="text-sm text-muted-foreground">
            Selecting more than one category is a good way to see the ranking clearly separate
            relevant from irrelevant candidates.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          <Input
            type="file"
            accept=".pdf,.txt"
            multiple
            disabled={uploading}
            onChange={(e) => handleFilesSelected(e.target.files)}
          />
          {uploadError && <p className="text-sm text-destructive">{uploadError}</p>}
          {uploading && <p className="text-sm text-muted-foreground">Uploading and parsing...</p>}
          <ul className="space-y-1">
            {value.uploadedCandidates.map((candidate) => (
              <li
                key={candidate.id}
                className="flex items-center justify-between rounded-md border px-3 py-2 text-sm"
              >
                <span>{candidate.filename}</span>
                <Button variant="ghost" size="sm" onClick={() => removeUploaded(candidate.id)}>
                  Remove
                </Button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
