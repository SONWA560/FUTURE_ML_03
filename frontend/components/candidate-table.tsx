"use client";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import type { CandidateResult } from "@/lib/api";

interface CandidateTableProps {
  candidates: CandidateResult[];
  onSelect: (candidate: CandidateResult) => void;
}

export function CandidateTable({ candidates, onSelect }: CandidateTableProps) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead className="w-14">Rank</TableHead>
          <TableHead>Candidate</TableHead>
          <TableHead className="w-40">Overall score</TableHead>
          <TableHead className="w-28 text-right">Skill match</TableHead>
          <TableHead className="w-28 text-right">Similarity</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {candidates.map((candidate) => (
          <TableRow
            key={candidate.id}
            className="cursor-pointer"
            onClick={() => onSelect(candidate)}
          >
            <TableCell className="font-medium">#{candidate.rank}</TableCell>
            <TableCell>
              <div className="flex flex-col gap-1">
                <span>
                  {candidate.source === "upload" ? "Uploaded candidate" : `Candidate ${candidate.id}`}
                </span>
                {candidate.category && (
                  <Badge variant="outline" className="w-fit text-xs">
                    {candidate.category}
                  </Badge>
                )}
              </div>
            </TableCell>
            <TableCell>
              <div className="flex items-center gap-2">
                <Progress value={candidate.final_score * 100} className="h-2" />
                <span className="w-10 text-sm tabular-nums">
                  {Math.round(candidate.final_score * 100)}%
                </span>
              </div>
            </TableCell>
            <TableCell className="text-right tabular-nums">
              {Math.round(candidate.skill_score * 100)}%
            </TableCell>
            <TableCell className="text-right tabular-nums">
              {Math.round(candidate.similarity_score * 100)}%
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
