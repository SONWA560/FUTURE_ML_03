const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface JobRoleSummary {
  id: string;
  title: string;
  category: string;
}

export interface JobDescription {
  id: string;
  title: string;
  category: string | null;
  description: string;
  required_skills: string[];
  preferred_skills: string[];
}

export interface SampleResume {
  id: string;
  category: string;
  text: string;
}

export interface UploadedCandidate {
  id: string;
  filename: string;
  text: string;
}

export interface CandidateResult {
  id: string;
  source: "sample" | "upload";
  category: string | null;
  rank: number;
  skill_score: number;
  similarity_score: number;
  final_score: number;
  matched_required_skills: string[];
  matched_preferred_skills: string[];
  missing_required_skills: string[];
  missing_preferred_skills: string[];
  explanation: string;
  text_snippet: string;
}

export interface ScreenResponse {
  job: JobDescription;
  candidates: CandidateResult[];
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      ...(init?.body && !(init.body instanceof FormData)
        ? { "Content-Type": "application/json" }
        : {}),
      ...init?.headers,
    },
  });

  if (!response.ok) {
    const detail = await response.json().catch(() => null);
    throw new Error(detail?.detail ?? `Request failed with status ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export function listJobRoles() {
  return apiFetch<JobRoleSummary[]>("/api/job-roles");
}

export function getJobRole(id: string) {
  return apiFetch<JobDescription>(`/api/job-roles/${id}`);
}

export function createCustomJob(title: string, description: string) {
  return apiFetch<JobDescription>("/api/job-roles/custom", {
    method: "POST",
    body: JSON.stringify({ title, description }),
  });
}

export function listCategories() {
  return apiFetch<string[]>("/api/resumes/categories");
}

export function getSampleResumes(category?: string, limit = 12) {
  const params = new URLSearchParams();
  if (category) params.set("category", category);
  params.set("limit", String(limit));
  return apiFetch<SampleResume[]>(`/api/resumes/sample?${params.toString()}`);
}

export async function uploadResume(file: File): Promise<UploadedCandidate> {
  const formData = new FormData();
  formData.append("file", file);
  return apiFetch<UploadedCandidate>("/api/resumes/upload", {
    method: "POST",
    body: formData,
  });
}

export interface ScreenParams {
  job: JobDescription;
  sampleResumeIds: string[];
  uploadedCandidates: UploadedCandidate[];
  skillWeight: number;
  similarityWeight: number;
}

export function screenCandidates(params: ScreenParams) {
  return apiFetch<ScreenResponse>("/api/screen", {
    method: "POST",
    body: JSON.stringify({
      job: params.job,
      sample_resume_ids: params.sampleResumeIds,
      uploaded_candidates: params.uploadedCandidates,
      skill_weight: params.skillWeight,
      similarity_weight: params.similarityWeight,
    }),
  });
}
