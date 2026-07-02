"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { CandidateTable } from "@/components/candidate-table";
import { CandidateDetailSheet } from "@/components/candidate-detail-sheet";
import { WeightSliders } from "@/components/weight-sliders";
import { useScreening } from "@/lib/screening-context";
import type { CandidateResult } from "@/lib/api";

export default function ResultsPage() {
  const { result } = useScreening();
  const [skillWeightPercent, setSkillWeightPercent] = useState(60);
  const [selectedCandidate, setSelectedCandidate] = useState<CandidateResult | null>(null);

  const rankedCandidates = useMemo(() => {
    if (!result) return [];
    const w1 = skillWeightPercent / 100;
    const w2 = 1 - w1;

    const rescored = result.candidates.map((candidate) => ({
      ...candidate,
      final_score: w1 + w2 === 0 ? 0.5 : w1 * candidate.skill_score + w2 * candidate.similarity_score,
    }));

    rescored.sort((a, b) => b.final_score - a.final_score);
    return rescored.map((candidate, index) => ({ ...candidate, rank: index + 1 }));
  }, [result, skillWeightPercent]);

  if (!result) {
    return (
      <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col items-center justify-center gap-4 px-4 py-10 text-center">
        <p className="text-muted-foreground">
          No screening results yet &mdash; set up a job role and some candidates first.
        </p>
        <Button asChild>
          <Link href="/">Back to setup</Link>
        </Button>
      </main>
    );
  }

  return (
    <main className="mx-auto flex w-full max-w-4xl flex-1 flex-col gap-6 px-4 py-10">
      <div className="flex items-center justify-between gap-4">
        <div className="space-y-1">
          <h1 className="text-2xl font-semibold tracking-tight">{result.job.title}</h1>
          <p className="text-muted-foreground">
            {rankedCandidates.length} candidate{rankedCandidates.length === 1 ? "" : "s"} screened
          </p>
        </div>
        <Button variant="outline" asChild>
          <Link href="/">New screening</Link>
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Required &amp; preferred skills</CardTitle>
          <CardDescription>{result.job.description}</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-2">
          {result.job.required_skills.map((skill) => (
            <Badge key={skill}>{skill}</Badge>
          ))}
          {result.job.preferred_skills.map((skill) => (
            <Badge key={skill} variant="outline">
              {skill}
            </Badge>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Adjust ranking weights</CardTitle>
          <CardDescription>
            Optional: re-weigh how much skill matching versus overall text similarity matters.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <WeightSliders skillWeightPercent={skillWeightPercent} onChange={setSkillWeightPercent} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Ranked candidates</CardTitle>
          <CardDescription>Click a candidate to see the full score breakdown.</CardDescription>
        </CardHeader>
        <CardContent>
          <CandidateTable candidates={rankedCandidates} onSelect={setSelectedCandidate} />
        </CardContent>
      </Card>

      <CandidateDetailSheet
        candidate={selectedCandidate}
        onOpenChange={(open) => !open && setSelectedCandidate(null)}
      />
    </main>
  );
}
