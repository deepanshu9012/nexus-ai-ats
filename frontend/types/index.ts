export interface Job {
  title: string;
  start_date: string;
  end_date: string;
}

export interface CandidateProfile {
  name: string;
  email: string;
  work_history: Job[];
  skills: string[];
  years_experience: number;
  education: string;
}

export interface SearchMatch {
  score: number;
  database_id: string;
  candidate_profile: CandidateProfile;
}

export interface SearchResponse {
  results: SearchMatch[];
}

export interface UploadResumeResponse {
  filename: string;
  database_id: string;
  candidate_profile: CandidateProfile;
}
