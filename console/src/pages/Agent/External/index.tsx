import { useState } from "react";
import {
  Card,
  Switch,
  Empty,
  Button,
  Modal,
  Form,
  Input,
  Drawer,
} from "@agentscope-ai/design";
import { useExternal } from "./useExternal";
import { useTranslation } from "react-i18next";
import type { ExternalAgentInfo } from "../../../api/types";
import { Plus, Trash2 } from "lucide-react";
import styles from "./index.module.less";

export default function ExternalPage() {
  const { t } = useTranslation();
  const { agents, loading, createAgent, updateAgent, toggleEnabled, deleteAgent } =
    useExternal();
  const [hoverKey, setHoverKey] = useState<string | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [editingAgent, setEditingAgent] = useState<ExternalAgentInfo | null>(
    null,
  );
  const [form] = Form.useForm();
  const [saving, setSaving] = useState(false);

  const handleCreate = () => {
    setEditingAgent(null);
    form.resetFields();
    form.setFieldsValue({
      stream: true,
      background: false,
      enabled: true,
    });
    setDrawerOpen(true);
  };

  const handleEdit = (agent: ExternalAgentInfo) => {
    setEditingAgent(agent);
    form.setFieldsValue({
      key: agent.key,
      name: agent.name,
      description: agent.description,
      url: agent.url,
      api_key: agent.api_key,
      stream: agent.stream,
      background: agent.background,
      enabled: agent.enabled,
    });
    setDrawerOpen(true);
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      setSaving(true);

      if (editingAgent) {
        const { key: _key, ...updates } = values;
        await updateAgent(editingAgent.key, updates);
      } else {
        const { key, ...agentData } = values;
        await createAgent(key, agentData);
      }
      setDrawerOpen(false);
    } catch {
      // validation error
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = (agent: ExternalAgentInfo) => {
    Modal.confirm({
      title: t("external.deleteConfirmTitle"),
      content: t("external.deleteConfirmContent", { name: agent.name }),
      okText: t("common.delete"),
      okButtonProps: { danger: true },
      cancelText: t("common.cancel"),
      onOk: () => deleteAgent(agent),
    });
  };

  return (
    <div className={styles.externalPage}>
      <div className={styles.pageHeader}>
        <div className={styles.breadcrumbHeader}>
          <span className={styles.breadcrumbParent}>Agent</span>
          <span className={styles.breadcrumbSeparator}>/</span>
          <span className={styles.breadcrumbCurrent}>
            {t("external.title")}
          </span>
        </div>
        <div className={styles.headerAction}>
          <Button
            type="primary"
            icon={<Plus size={16} />}
            onClick={handleCreate}
          >
            {t("external.create")}
          </Button>
        </div>
      </div>

      <div className={styles.agentsContainer}>
        {loading ? (
          <div className={styles.loading}>
            <p>{t("common.loading")}</p>
          </div>
        ) : agents.length === 0 ? (
          <Empty description={t("external.emptyState")} />
        ) : (
          <div className={styles.agentsGrid}>
            {agents.map((agent) => (
              <Card
                key={agent.key}
                className={`${styles.agentCard} ${
                  agent.enabled ? styles.enabledCard : ""
                } ${
                  hoverKey === agent.key ? styles.hoverCard : styles.normalCard
                }`}
                onMouseEnter={() => setHoverKey(agent.key)}
                onMouseLeave={() => setHoverKey(null)}
                onClick={() => handleEdit(agent)}
              >
                <div className={styles.cardHeader}>
                  <h3 className={styles.agentName}>{agent.name}</h3>
                  <div className={styles.statusContainer}>
                    <span className={styles.statusDot} />
                    <span className={styles.statusText}>
                      {agent.enabled
                        ? t("common.enabled")
                        : t("common.disabled")}
                    </span>
                  </div>
                </div>

                <p className={styles.agentDescription}>
                  {agent.description || agent.url}
                </p>

                <div className={styles.cardFooter}>
                  <Button
                    type="text"
                    danger
                    size="small"
                    icon={<Trash2 size={14} />}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDelete(agent);
                    }}
                    className={styles.deleteBtn}
                  />
                  <Switch
                    checked={agent.enabled}
                    onChange={(_checked, e) => {
                      e.stopPropagation();
                      toggleEnabled(agent);
                    }}
                  />
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>

      <Drawer
        title={
          editingAgent ? t("external.editTitle") : t("external.createTitle")
        }
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        width={480}
        extra={
          <Button type="primary" onClick={handleSubmit} loading={saving}>
            {t("common.save")}
          </Button>
        }
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="key"
            label={t("external.fieldKey")}
            rules={[
              { required: true, message: t("external.fieldKeyRequired") },
              {
                pattern: /^[a-zA-Z0-9_-]+$/,
                message: t("external.fieldKeyPattern"),
              },
            ]}
          >
            <Input
              placeholder={t("external.fieldKeyPlaceholder")}
              disabled={!!editingAgent}
            />
          </Form.Item>

          <Form.Item
            name="name"
            label={t("external.fieldName")}
            rules={[
              { required: true, message: t("external.fieldNameRequired") },
            ]}
          >
            <Input placeholder={t("external.fieldNamePlaceholder")} />
          </Form.Item>

          <Form.Item name="description" label={t("external.fieldDescription")}>
            <Input.TextArea
              rows={2}
              placeholder={t("external.fieldDescriptionPlaceholder")}
            />
          </Form.Item>

          <Form.Item
            name="url"
            label={t("external.fieldUrl")}
            rules={[
              { required: true, message: t("external.fieldUrlRequired") },
            ]}
          >
            <Input placeholder={t("external.fieldUrlPlaceholder")} />
          </Form.Item>

          <Form.Item name="api_key" label={t("external.fieldApiKey")}>
            <Input.Password
              placeholder={t("external.fieldApiKeyPlaceholder")}
            />
          </Form.Item>

          <Form.Item
            name="stream"
            label={t("external.fieldStream")}
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>

          <Form.Item
            name="background"
            label={t("external.fieldBackground")}
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>
        </Form>
      </Drawer>
    </div>
  );
}
