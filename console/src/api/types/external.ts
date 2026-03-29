/**
 * External agent types
 */

export interface ExternalAgentInfo {
  /** Unique agent key identifier */
  key: string;
  /** Agent display name */
  name: string;
  /** Agent description */
  description: string;
  /** Whether the agent is enabled */
  enabled: boolean;
  /** Agent API endpoint URL */
  url: string;
  /** API key (masked) */
  api_key: string;
  /** HTTP headers */
  headers: Record<string, string>;
  /** Enable streaming output */
  stream: boolean;
  /** Enable async execution */
  background: boolean;
}

export interface ExternalAgentCreateRequest {
  /** Unique agent key identifier */
  agent_key: string;
  /** Agent configuration */
  agent: {
    /** Agent display name */
    name: string;
    /** Agent description */
    description?: string;
    /** Whether to enable the agent */
    enabled?: boolean;
    /** Agent API endpoint URL */
    url?: string;
    /** API key */
    api_key?: string;
    /** HTTP headers */
    headers?: Record<string, string>;
    /** Enable streaming output */
    stream?: boolean;
    /** Enable async execution */
    background?: boolean;
  };
}

export interface ExternalAgentUpdateRequest {
  /** Agent display name */
  name?: string;
  /** Agent description */
  description?: string;
  /** Whether to enable the agent */
  enabled?: boolean;
  /** Agent API endpoint URL */
  url?: string;
  /** API key */
  api_key?: string;
  /** HTTP headers */
  headers?: Record<string, string>;
  /** Enable streaming output */
  stream?: boolean;
  /** Enable async execution */
  background?: boolean;
}
