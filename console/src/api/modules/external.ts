import { request } from "../request";
import type {
  ExternalAgentInfo,
  ExternalAgentCreateRequest,
  ExternalAgentUpdateRequest,
} from "../types";

export const externalApi = {
  /**
   * List all external agents
   */
  listExternalAgents: () => request<ExternalAgentInfo[]>("/external"),

  /**
   * Get details of a specific external agent
   */
  getExternalAgent: (agentKey: string) =>
    request<ExternalAgentInfo>(
      `/external/${encodeURIComponent(agentKey)}`,
    ),

  /**
   * Create a new external agent
   */
  createExternalAgent: (body: ExternalAgentCreateRequest) =>
    request<ExternalAgentInfo>("/external", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  /**
   * Update an existing external agent
   */
  updateExternalAgent: (
    agentKey: string,
    body: ExternalAgentUpdateRequest,
  ) =>
    request<ExternalAgentInfo>(
      `/external/${encodeURIComponent(agentKey)}`,
      {
        method: "PUT",
        body: JSON.stringify(body),
      },
    ),

  /**
   * Toggle external agent enabled status
   */
  toggleExternalAgent: (agentKey: string) =>
    request<ExternalAgentInfo>(
      `/external/${encodeURIComponent(agentKey)}/toggle`,
      {
        method: "PATCH",
      },
    ),

  /**
   * Delete an external agent
   */
  deleteExternalAgent: (agentKey: string) =>
    request<{ message: string }>(
      `/external/${encodeURIComponent(agentKey)}`,
      {
        method: "DELETE",
      },
    ),
};
