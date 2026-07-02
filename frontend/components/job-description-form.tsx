"use client";

import { useEffect, useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { listJobRoles, type JobRoleSummary } from "@/lib/api";

export type JobSetup =
  | { mode: "curated"; roleId: string }
  | { mode: "custom"; title: string; description: string };

interface JobDescriptionFormProps {
  value: JobSetup;
  onChange: (value: JobSetup) => void;
}

export function JobDescriptionForm({ value, onChange }: JobDescriptionFormProps) {
  const [roles, setRoles] = useState<JobRoleSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listJobRoles()
      .then((fetchedRoles) => {
        setRoles(fetchedRoles);
        if (fetchedRoles.length > 0 && value.mode === "curated" && !value.roleId) {
          onChange({ mode: "curated", roleId: fetchedRoles[0].id });
        }
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <Tabs
      value={value.mode}
      onValueChange={(mode) =>
        onChange(
          mode === "curated"
            ? { mode: "curated", roleId: roles[0]?.id ?? "" }
            : { mode: "custom", title: "", description: "" }
        )
      }
    >
      <TabsList>
        <TabsTrigger value="curated">Choose a role</TabsTrigger>
        <TabsTrigger value="custom">Paste your own</TabsTrigger>
      </TabsList>

      <TabsContent value="curated" className="space-y-3 pt-2">
        <Label htmlFor="role-select">Job role</Label>
        {error && <p className="text-sm text-destructive">Could not load job roles: {error}</p>}
        <Select
          disabled={loading}
          value={value.mode === "curated" ? value.roleId : undefined}
          onValueChange={(roleId) => onChange({ mode: "curated", roleId })}
        >
          <SelectTrigger id="role-select" className="w-full">
            <SelectValue placeholder={loading ? "Loading roles..." : "Select a role"} />
          </SelectTrigger>
          <SelectContent>
            {roles.map((role) => (
              <SelectItem key={role.id} value={role.id}>
                {role.title}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <p className="text-sm text-muted-foreground">
          Curated roles come with a pre-defined list of required and preferred skills, based on
          typical requirements for that role.
        </p>
      </TabsContent>

      <TabsContent value="custom" className="space-y-3 pt-2">
        <div className="space-y-2">
          <Label htmlFor="custom-title">Job title</Label>
          <Input
            id="custom-title"
            placeholder="e.g. Senior Data Analyst"
            value={value.mode === "custom" ? value.title : ""}
            onChange={(e) =>
              onChange({
                mode: "custom",
                title: e.target.value,
                description: value.mode === "custom" ? value.description : "",
              })
            }
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="custom-description">Job description</Label>
          <Textarea
            id="custom-description"
            rows={6}
            placeholder="Paste the full job description here..."
            value={value.mode === "custom" ? value.description : ""}
            onChange={(e) =>
              onChange({
                mode: "custom",
                title: value.mode === "custom" ? value.title : "",
                description: e.target.value,
              })
            }
          />
        </div>
        <p className="text-sm text-muted-foreground">
          Required skills will be detected automatically from the text you paste in.
        </p>
      </TabsContent>
    </Tabs>
  );
}
