import { useCallback, useEffect, useState } from 'react'
import { Button, Card, Col, Form, Input, Modal, Row, Select, Space, Table, Tooltip, message } from 'antd'
import { PlusOutlined, StopOutlined, PlayCircleOutlined, DeleteOutlined, EditOutlined } from '@ant-design/icons'
import { catalogService } from '../services/catalogService'
import type { CatalogItem, CatalogName, ToolProcessLink } from '../types/catalog'
import { CATALOG_LABELS, CATALOG_COLOR_PALETTE } from '../types/catalog'
import StatusTag from '../components/common/StatusTag'
import { clientColumnFilter, clientTextColumnFilter } from '../components/common/columnFilters'
import { useAuthStore } from '../store/authStore'
import { palette } from '../theme'

const CATALOGS: CatalogName[] = ['tools', 'processes', 'resolution-types', 'record-types', 'teams', 'access-types']

function CatalogCard({ catalog }: { catalog: CatalogName }) {
  const { hasPermission } = useAuthStore()
  const canCreate = hasPermission('catalogs', 'create')
  const canDeactivate = hasPermission('catalogs', 'deactivate')
  const [items, setItems] = useState<CatalogItem[]>([])
  const [loading, setLoading] = useState(false)
  const [form] = Form.useForm<{ name: string }>()
  const [editingItem, setEditingItem] = useState<CatalogItem | null>(null)
  const [renameForm] = Form.useForm<{ name: string }>()

  const load = useCallback(async () => {
    setLoading(true)
    try {
      setItems((await catalogService.list(catalog, 'all')).items)
    } finally {
      setLoading(false)
    }
  }, [catalog])

  useEffect(() => { load() }, [load])

  const apiError = (err: unknown, fallback: string) =>
    (err as { response?: { data?: { message?: string } } }).response?.data?.message ?? fallback

  const handleAdd = async ({ name }: { name: string }) => {
    try {
      await catalogService.create(catalog, name.trim())
      form.resetFields()
      load()
    } catch (err: unknown) {
      message.error(apiError(err, 'Error al agregar el valor'))
    }
  }

  const toggle = async (item: CatalogItem) => {
    try {
      if (item.active) await catalogService.deactivate(catalog, item.id)
      else await catalogService.activate(catalog, item.id)
      load()
    } catch (err: unknown) {
      message.error(apiError(err, 'No se pudo cambiar el estado'))
    }
  }

  const openRename = (item: CatalogItem) => {
    setEditingItem(item)
    renameForm.setFieldsValue({ name: item.name })
  }

  const handleRename = async ({ name }: { name: string }) => {
    if (!editingItem) return
    try {
      await catalogService.rename(catalog, editingItem.id, name.trim())
      setEditingItem(null)
      load()
    } catch (err: unknown) {
      message.error(apiError(err, 'No se pudo renombrar el valor'))
    }
  }

  return (
    <Card title={CATALOG_LABELS[catalog]} size="small">
      <Table
        rowKey="id" size="small" loading={loading} dataSource={items} pagination={false}
        columns={[
          ...(catalog === 'access-types' ? [{
            title: '', dataIndex: 'color_index', width: 32,
            render: (v: number | undefined) => (
              <span style={{
                display: 'inline-block', width: 12, height: 12, borderRadius: 3,
                background: CATALOG_COLOR_PALETTE[(v ?? 0) % CATALOG_COLOR_PALETTE.length],
              }} />
            ),
          }] : []),
          {
            title: 'Nombre', dataIndex: 'name',
            ...clientTextColumnFilter<CatalogItem>('Buscar nombre...', r => r.name),
          },
          {
            title: 'Estado', dataIndex: 'active', width: 90, render: (v: boolean) => <StatusTag active={v} />,
            ...clientColumnFilter<CatalogItem>(
              [{ text: 'Activo', value: 'true' }, { text: 'Inactivo', value: 'false' }],
              (value, record) => String(record.active) === value,
            ),
          },
          ...(canCreate ? [{
            title: '', key: 'edit', width: 40,
            render: (_: unknown, item: CatalogItem) => (
              <Tooltip title="Editar nombre">
                <Button size="small" icon={<EditOutlined />} onClick={() => openRename(item)} />
              </Tooltip>
            ),
          }] : []),
          ...(canDeactivate ? [{
            title: '', key: 'toggle', width: 60,
            render: (_: unknown, item: CatalogItem) => (
              <Tooltip title={item.active ? 'Desactivar' : 'Activar'}>
                <Button size="small" danger={item.active}
                  icon={item.active ? <StopOutlined /> : <PlayCircleOutlined style={{ color: palette.green600 }} />}
                  onClick={() => toggle(item)} />
              </Tooltip>
            ),
          }] : []),
        ]}
      />
      <Modal title="Editar nombre" open={!!editingItem} onCancel={() => setEditingItem(null)}
        onOk={() => renameForm.submit()} okText="Guardar" destroyOnHidden>
        <Form form={renameForm} layout="vertical" onFinish={handleRename}>
          <Form.Item name="name" label="Nombre" rules={[{ required: true, message: 'Nombre requerido' }]}>
            <Input />
          </Form.Item>
        </Form>
      </Modal>
      {canCreate && (
        <Form form={form} layout="inline" onFinish={handleAdd} style={{ marginTop: 8 }}>
          <Form.Item name="name" rules={[{ required: true, message: 'Nombre requerido' }]}>
            <Input placeholder="Nuevo valor" style={{ width: 180 }} />
          </Form.Item>
          <Form.Item>
            <Button htmlType="submit" icon={<PlusOutlined />}>Agregar</Button>
          </Form.Item>
        </Form>
      )}
    </Card>
  )
}

/** OBS-0049: vínculos sugeridos Herramienta↔Proceso — guía no restrictiva para el selector de
 * Proceso en el formulario de ticket una vez elegida la Herramienta (no bloquea otras combinaciones). */
function ToolProcessLinksCard() {
  const { hasPermission } = useAuthStore()
  const canCreate = hasPermission('catalogs', 'create')
  const canDeactivate = hasPermission('catalogs', 'deactivate')
  const [tools, setTools] = useState<CatalogItem[]>([])
  const [processes, setProcesses] = useState<CatalogItem[]>([])
  const [links, setLinks] = useState<ToolProcessLink[]>([])
  const [loading, setLoading] = useState(false)
  const [form] = Form.useForm<{ tool_id: string; process_id: string }>()

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const [toolsRes, processesRes, linksRes] = await Promise.all([
        catalogService.list('tools', 'true'),
        catalogService.list('processes', 'true'),
        catalogService.listToolProcesses(),
      ])
      setTools(toolsRes.items)
      setProcesses(processesRes.items)
      setLinks(linksRes.items)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  const nameOf = (items: CatalogItem[], id: string) => items.find(i => i.id === id)?.name ?? id

  const handleLink = async ({ tool_id, process_id }: { tool_id: string; process_id: string }) => {
    try {
      await catalogService.linkToolProcess(tool_id, process_id)
      form.resetFields()
      load()
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { message?: string } } }).response?.data?.message
        ?? 'Error al crear el vínculo'
      message.error(msg)
    }
  }

  const handleUnlink = async (link: ToolProcessLink) => {
    try {
      await catalogService.unlinkToolProcess(link.tool_id, link.process_id)
      load()
    } catch {
      message.error('No se pudo quitar el vínculo')
    }
  }

  return (
    <Card title="Vínculos Herramienta ↔ Proceso" size="small">
      <Table
        rowKey={r => `${r.tool_id}:${r.process_id}`} size="small" loading={loading}
        dataSource={links} pagination={false}
        columns={[
          { title: 'Herramienta', dataIndex: 'tool_id', render: (v: string) => nameOf(tools, v) },
          { title: 'Proceso', dataIndex: 'process_id', render: (v: string) => nameOf(processes, v) },
          ...(canDeactivate ? [{
            title: '', key: 'remove', width: 60,
            render: (_: unknown, link: ToolProcessLink) => (
              <Tooltip title="Quitar vínculo">
                <Button size="small" danger icon={<DeleteOutlined />} onClick={() => handleUnlink(link)} />
              </Tooltip>
            ),
          }] : []),
        ]}
      />
      {canCreate && (
        <Form form={form} layout="inline" onFinish={handleLink} style={{ marginTop: 8 }}>
          <Form.Item name="tool_id" rules={[{ required: true, message: 'Herramienta requerida' }]}>
            <Select placeholder="Herramienta" style={{ width: 180 }}
              options={tools.map(t => ({ value: t.id, label: t.name }))} />
          </Form.Item>
          <Form.Item name="process_id" rules={[{ required: true, message: 'Proceso requerido' }]}>
            <Select placeholder="Proceso" style={{ width: 180 }}
              options={processes.map(p => ({ value: p.id, label: p.name }))} />
          </Form.Item>
          <Form.Item>
            <Button htmlType="submit" icon={<PlusOutlined />}>Vincular</Button>
          </Form.Item>
        </Form>
      )}
    </Card>
  )
}

export default function CatalogsPage() {
  return (
    <Space direction="vertical" size={16} style={{ width: '100%' }}>
      <Row gutter={[16, 16]}>
        {CATALOGS.map(c => (
          <Col key={c} xs={24} lg={8}>
            <CatalogCard catalog={c} />
          </Col>
        ))}
      </Row>
      <ToolProcessLinksCard />
    </Space>
  )
}
