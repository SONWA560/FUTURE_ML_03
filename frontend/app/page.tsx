"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { JobDescriptionForm, type JobSetup } from "@/components/job-description-form";
import { ResumePicker, type ResumeSetup } from "@/components/resume-picker";
import { useScreening } from "@/lib/screening-context";
import { createCustomJob, getJobRole, getSampleResumes, screenCandidates } from "@/lib/api";

export default function HomePage() {
  const router = useRouter();
  const { setResult } = useScreening();

  const [jobSetup, setJobSetup] = useState<JobSetup>({ mode: "curated", roleId: "" });
  const [resumeSetup, setResumeSetup] = useState<ResumeSetup>({
    mode: "sample",
    selectedCategories: [],
    perCategoryLimit: 8,
    uploadedCandidates: [],
  });
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const hasCandidates =
    resumeSetup.mode === "sample"
      ? resumeSetup.selectedCategories.length > 0
      : resumeSetup.uploadedCandidates.length > 0;

  const jobReady =
    jobSetup.mode === "curated"
      ? Boolean(jobSetup.roleId)
      : jobSetup.title.trim().length > 0 && jobSetup.description.trim().length > 0;

  async function handleRunScreening() {
    setError(null);
    setRunning(true);
    try {
      const job =
        jobSetup.mode === "curated"
          ? await getJobRole(jobSetup.roleId)
          : await createCustomJob(jobSetup.title, jobSetup.description);

      let sampleResumeIds: string[] = [];
      if (resumeSetup.mode === "sample") {
        const resumesByCategory = await Promise.all(
          resumeSetup.selectedCategories.map((category) =>
            getSampleResumes(category, resumeSetup.perCategoryLimit)
          )
        );
        sampleResumeIds = resumesByCategory.flat().map((resume) => resume.id);
      }

      const result = await screenCandidates({
        job,
        sampleResumeIds,
        uploadedCandidates: resumeSetup.mode === "upload" ? resumeSetup.uploadedCandidates : [],
        skillWeight: 0.6,
        similarityWeight: 0.4,
      });

      setResult(result);
      router.push("/results");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong whilst screening");
    } finally {
      setRunning(false);
    }
  }

  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col gap-6 px-4 py-10">
      <div className="space-y-2">
        <h1 className="text-3xl font-semibold tracking-tight">Resume Screening &amp; Ranking</h1>
        <p className="text-muted-foreground">
          Choose a job role and a set of candidate resumes, and we&apos;ll rank them by how well
          they match &mdash; with a plain-English explanation and a list of missing skills for
          each candidate.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>1. Job role</CardTitle>
          <CardDescription>Pick a curated role or paste your own job description.</CardDescription>
        </CardHeader>
        <CardContent>
          <JobDescriptionForm value={jobSetup} onChange={setJobSetup} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>2. Candidate resumes</CardTitle>
          <CardDescription>
            Use sample resumes from our dataset, or upload your own PDF/text files.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ResumePicker value={resumeSetup} onChange={setResumeSetup} />
        </CardContent>
      </Card>

      {error && <p className="text-sm text-destructive">{error}</p>}

      <Button
        size="lg"
        disabled={!jobReady || !hasCandidates || running}
        onClick={handleRunScreening}
      >
        {running ? "Screening..." : "Run screening"}
      </Button>
    </main>
  );
}
