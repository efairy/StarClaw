import { useCallback, useEffect, useState } from "react";
import { message } from "@agentscope-ai/design";
import api from "../../../api";
import type { ExternalAgentInfo } from "../../../api/types";
import { useTranslation } from "react-i18next";
import { useAgentStore } from "../../../stores/agentStore";

export function useExternal() {
  const { t } = useTranslation();
  const { selectedAgent } = useAgentStore();
  const [agents, setAgents] = useState<ExternalAgentInfo[]>([]);
  const [loading, setLoading] = useState(false);

  const loadAgents = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.listExternalAgents();
      setAgents(data);
    } catch (error) {
      console.error("Failed to load external agents:", error);
      message.error(t("external.loadError"));
    } finally {
      setLoading(false);
    }
  }, [t]);

  useEffect(() => {
    loadAgents();
  }, [loadAgents, selectedAgent]);

  const createAgent = useCallback(
    async (
      key: string,
      agentData: {
        name: string;
        description?: string;
        enabled?: boolean;
        url?: string;
        api_key?: string;
        headers?: Record<string, string>;
        stream?: boolean;
        background?: boolean;
      },
    ) => {
      try {
        await api.createExternalAgent({
          agent_key: key,
          agent: agentData,
        });
        message.success(t("external.createSuccess"));
        await loadAgents();
        return true;
      } catch (error: any) {
        const errorMsg = error?.message || t("external.createError");
        message.error(errorMsg);
        return false;
      }
    },
    [t, loadAgents],
  );

  const updateAgent = useCallback(
    async (
      key: string,
      updates: {
        name?: string;
        description?: string;
        enabled?: boolean;
        url?: string;
        api_key?: string;
        headers?: Record<string, string>;
        stream?: boolean;
        background?: boolean;
      },
    ) => {
      try {
        await api.updateExternalAgent(key, updates);
        message.success(t("external.updateSuccess"));
        await loadAgents();
        return true;
      } catch (error: any) {
        const errorMsg = error?.message || t("external.updateError");
        message.error(errorMsg);
        return false;
      }
    },
    [t, loadAgents],
  );

  const toggleEnabled = useCallback(
    async (agent: ExternalAgentInfo) => {
      try {
        await api.toggleExternalAgent(agent.key);
        message.success(
          agent.enabled
            ? t("external.disableSuccess")
            : t("external.enableSuccess"),
        );
        await loadAgents();
      } catch (error) {
        message.error(t("external.toggleError"));
      }
    },
    [t, loadAgents],
  );

  const deleteAgent = useCallback(
    async (agent: ExternalAgentInfo) => {
      try {
        await api.deleteExternalAgent(agent.key);
        message.success(t("external.deleteSuccess"));
        await loadAgents();
      } catch (error) {
        message.error(t("external.deleteError"));
      }
    },
    [t, loadAgents],
  );

  return {
    agents,
    loading,
    createAgent,
    updateAgent,
    toggleEnabled,
    deleteAgent,
  };
}
