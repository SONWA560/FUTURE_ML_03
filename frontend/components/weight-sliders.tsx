"use client";

import { Slider } from "@/components/ui/slider";
import { Label } from "@/components/ui/label";

interface WeightSlidersProps {
  skillWeightPercent: number;
  onChange: (skillWeightPercent: number) => void;
}

export function WeightSliders({ skillWeightPercent, onChange }: WeightSlidersProps) {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-sm">
        <Label>Skill match importance</Label>
        <span className="text-muted-foreground">
          {skillWeightPercent}% skills / {100 - skillWeightPercent}% text similarity
        </span>
      </div>
      <Slider
        value={[skillWeightPercent]}
        onValueChange={([value]) => onChange(value)}
        min={0}
        max={100}
        step={5}
      />
      <p className="text-xs text-muted-foreground">
        Adjust how much weight is given to matched skills versus overall resume-to-job text
        similarity. The ranking below updates instantly &mdash; no re-upload needed.
      </p>
    </div>
  );
}
