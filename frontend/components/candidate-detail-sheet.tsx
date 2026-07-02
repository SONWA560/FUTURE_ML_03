"use client";

import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ScoreBreakdownChart } from "@/components/score-breakdown-chart";
import type { CandidateResult } from "@/lib/api";

interface CandidateDetailSheetProps {
  candidate: CandidateResult | null;
  onOpenChange: (open: boolean) => void;
}

export function CandidateDetailSheet({ candidate, onOpenChange }: CandidateDetailSheetProps) {
  return (
    <Sheet open={Boolean(candidate)} onOpenChange={onOpenChange}>
      <SheetContent className="w-full sm:max-w-lg overflow-y-auto">
        {candidate && (
          <div className="flex flex-col gap-6 p-6">
            <SheetHeader className="p-0">
              <SheetTitle>
                Candidate {candidate.id}
                {candidate.category ? ` — ${candidate.category}` : ""}
              </SheetTitle>
              <SheetDescription>
                Rank #{candidate.rank} &middot; Overall score {Math.round(candidate.final_score * 100)}%
              </SheetDescription>
            </SheetHeader>

            <div className="space-y-2">
              <h3 className="text-sm font-medium">Score breakdown</h3>
              <ScoreBreakdownChart
                skillScore={candidate.skill_score}
                similarityScore={candidate.similarity_score}
              />
            </div>

            <Separator />

            <div className="space-y-3">
              <h3 className="text-sm font-medium">Why this ranking?</h3>
              <p className="text-sm text-muted-foreground">{candidate.explanation}</p>
            </div>

            <Separator />

            <div className="space-y-3">
              <h3 className="text-sm font-medium">Matched skills</h3>
              <div className="flex flex-wrap gap-2">
                {[...candidate.matched_required_skills, ...candidate.matched_preferred_skills].map(
                  (skill) => (
                    <Badge key={skill} variant="secondary">
                      {skill}
                    </Badge>
                  )
                )}
                {candidate.matched_required_skills.length === 0 &&
                  candidate.matched_preferred_skills.length === 0 && (
                    <p className="text-sm text-muted-foreground">No listed skills matched.</p>
                  )}
              </div>
            </div>

            <div className="space-y-3">
              <h3 className="text-sm font-medium">Missing skills</h3>
              <div className="flex flex-wrap gap-2">
                {[...candidate.missing_required_skills, ...candidate.missing_preferred_skills].map(
                  (skill) => (
                    <Badge key={skill} variant="outline" className="border-destructive/50 text-destructive">
                      {skill}
                    </Badge>
                  )
                )}
                {candidate.missing_required_skills.length === 0 &&
                  candidate.missing_preferred_skills.length === 0 && (
                    <p className="text-sm text-muted-foreground">
                      No required or preferred skills are missing.
                    </p>
                  )}
              </div>
            </div>

            <Separator />

            <div className="space-y-2">
              <h3 className="text-sm font-medium">Resume excerpt</h3>
              <ScrollArea className="h-40 rounded-md border p-3">
                <p className="text-sm text-muted-foreground whitespace-pre-line">
                  {candidate.text_snippet}
                </p>
              </ScrollArea>
            </div>
          </div>
        )}
      </SheetContent>
    </Sheet>
  );
}
