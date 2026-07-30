import { useCallback, useEffect, useState } from 'react'
import { Alert, App, Button, Descriptions, Form, Input, Modal, Row, Col, Segmented, Select, Space, Table, Tooltip, Upload } from 'antd'
import {
  PlusOutlined, EyeOutlined, UserSwitchOutlined, InboxOutlined, ThunderboltOutlined,
  ClockCircleOutlined, CheckCircleOutlined, FieldTimeOutlined, UploadOutlined,
} from '@ant-design/icons'
import type { ColumnsType, TableProps } from 'antd/es/table'
import type { DefaultOptionType } from 'antd/es/select'
import type { UploadFile } from 'antd'
import { useNavigate } from 'react-router-dom'
import SortIndicator from '../components/tickets/SortIndicator'
import { ticketService } from '../services/ticketService'
import { clientService } from '../services/clientService'
import { projectService } from '../services/projectService'
import { clientContactService } from '../services/clientContactService'
import { catalogService } from '../services/catalogService'
import { resourceService, skillService } from '../services/resourceService'
import { taskListService } from '../services/taskListService'
import { slaService } from '../services/slaService'
import type { SlaRule } from '../types/sla'
import type {
  TicketListItem, TicketFormData, TicketStatus, Priority, Severity,
} from '../types/ticket'
import { STATUS_LABELS, TICKET_TYPE_LABELS, PRIORITY_LABELS, SEVERITY_LABELS } from '../types/ticket'
import type { CatalogItem, ToolProcessLink } from '../types/catalog'
import type { ClientListItem } from '../types/client'
import type { ProjectListItem } from '../types/project'
import type { Resource, Skill } from '../types/resource'
import type { ClientContact } from '../types/clientContact'
import type { TaskList } from '../types/taskList'
import { vivid } from '../theme'
import TicketStatusTag from '../components/tickets/TicketStatusTag'
import SlaStatusTag from '../components/tickets/SlaStatusTag'
import PriorityBadge from '../components/tickets/PriorityBadge'
import AssignModal from '../components/tickets/AssignModal'
import PageToolbar from '../components/common/PageToolbar'
import StatCard from '../components/common/StatCard'
import SavedFiltersBar from '../components/tickets/SavedFiltersBar'
import { textColumnFilter, serverColumnFilter } from '../components/common/columnFilters'
import { useAuthStore } from '../store/authStore'
import type { TicketFilterCriteria } from '../store/savedFiltersStore'
import RichTextEditor, { isRichTextEmpty } from '../components/tickets/RichTextEditor'
import { mapApiErrorToFormFields, type FieldErrorRule } from '../services/formErrorMapper'

// OBS-0034 (spec 028): mismos rangos Unicode que `backend/domain/services/ticket_service.py`
// (`_EMOJI_RANGES`) — letras (incl. acentos/ñ), números y puntuación común quedan permitidos.
const EMOJI_PATTERN = /[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}\u{1F1E6}-\u{1F1FF}\u{FE0F}\u{200D}]/u

const TITLE_RULES = [
  { required: true, whitespace: true, message: 'El título es requerido' },
  {
    validator: (_: unknown, value: string) =>
      value && EMOJI_PATTERN.test(value)
        ? Promise.reject(new Error('El título no admite emojis'))
        : Promise.resolve(),
  },
]

// OBS-0018: asocia códigos de error de la API a los campos del formulario de creación de Ticket/Tarea.
const TICKET_ERROR_RULES: FieldErrorRule[] = [
  // OBS-0033/OBS-0034 (spec 028): título vacío/solo espacios o con emojis.
  { code: 'title_blank', field: 'title' },
  { code: 'title_invalid_chars', field: 'title' },
  { code: 'validation_error', field: 'client_id', messageIncludes: ['client_id'] },
  // OBS-0045: project_id/client_contact_id obligatorios al crear un Ticket desde perfil interno.
  { code: 'validation_error', field: 'project_id', messageIncludes: ["'project_id'", 'proyecto no pertenece'] },
  { code: 'validation_error', field: 'client_contact_id', messageIncludes: ["'client_contact_id'"] },
  { code: 'client_inactive', field: 'client_id' },
  { code: 'project_inactive', field: 'project_id' },
  { code: 'project_not_assigned', field: 'project_id' },
  { code: 'catalog_inactive', field: 'tool_id', messageIncludes: ['herramienta'] },
  { code: 'catalog_inactive', field: 'process_id', messageIncludes: ['proceso'] },
  { code: 'catalog_inactive', field: 'record_type_id', messageIncludes: ['tipo de registro'] },
  { code: 'client_contact_mismatch', field: 'client_contact_id' },
  { code: 'contact_not_in_project', field: 'client_contact_id' },
  { code: 'list_mismatch', field: 'list_id' },
]

const IN_PROGRESS_STATUSES: TicketStatus[] = ['contacto', 'en_analisis', 'en_ejecucion', 'en_pruebas']

const statusOptions = Object.entries(STATUS_LABELS).map(([value, label]) => ({ value, label }))
const priorityOptions = Object.entries(PRIORITY_LABELS).map(([value, label]) => ({ value, label }))
const severityOptions = Object.entries(SEVERITY_LABELS).map(([value, label]) => ({ value, label }))
const typeOptions = Object.entries(TICKET_TYPE_LABELS).map(([value, label]) => ({ value, label }))
const SLA_STATUS_OPTIONS = [
  { text: 'Corriendo', value: 'corriendo' },
  { text: 'Pausado', value: 'pausado' },
  { text: 'Vencido', value: 'vencido' },
  { text: 'Detenido', value: 'detenido' },
  { text: 'Sin SLA', value: 'sin_sla' },
]

export default function TicketsPage() {
  const { message } = App.useApp()
  const { hasPermission, role } = useAuthStore()
  const navigate = useNavigate()
  const canCreate = hasPermission('tickets', 'create')
  const canAssign = hasPermission('tickets', 'assign')
  // OBS-0047/0048 (spec 033): "Skills requeridas" pasa a un permiso dedicado (solo Coordinador)
  // en vez de tickets:edit — Admin/QM crean tickets sin poder fijar Skills requeridas (las puede
  // agregar después un Coordinador desde el detalle del ticket).
  const canManageSkills = hasPermission('tickets', 'manage_skills')
  /** Usuario/cliente (Fase 2.1 US3, renombrado spec 010): alta simplificada (solo título/descripción), sin acceso a
   * catálogos/clientes/recursos internos — el backend ya filtra su listado a lo propio. */
  const isEncargado = role?.name === 'Usuario/cliente'

  const [tickets, setTickets] = useState<TicketListItem[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(false)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<TicketStatus[]>([])
  const [clientFilter, setClientFilter] = useState<string | undefined>()
  const [priorityFilter, setPriorityFilter] = useState<Priority | undefined>()
  const [severityFilter, setSeverityFilter] = useState<Severity | undefined>()
  const [assigneeFilter, setAssigneeFilter] = useState<string | undefined>()
  const [slaStatusFilter, setSlaStatusFilter] = useState<TicketListItem['sla']['status'] | undefined>()
  const [sort, setSort] = useState('urgency')
  const [assigningId, setAssigningId] = useState<string | null>(null)
  const [stats, setStats] = useState<{ nuevo: number; enProgreso: number; pendienteUsuario: number; resuelto: number; vencenHoy: number } | null>(null)

  const [clients, setClients] = useState<ClientListItem[]>([])
  const [projects, setProjects] = useState<ProjectListItem[]>([])
  const [projectSlaRules, setProjectSlaRules] = useState<SlaRule[]>([])
  const [myProjects, setMyProjects] = useState<ProjectListItem[]>([])
  const [contacts, setContacts] = useState<ClientContact[]>([])
  const [tools, setTools] = useState<CatalogItem[]>([])
  const [processes, setProcesses] = useState<CatalogItem[]>([])
  // OBS-0049: vínculos sugeridos Herramienta↔Proceso (guía, no restricción).
  const [toolProcessLinks, setToolProcessLinks] = useState<ToolProcessLink[]>([])
  const [resources, setResources] = useState<Resource[]>([])
  const [skills, setSkills] = useState<Skill[]>([])
  const [recordTypes, setRecordTypes] = useState<CatalogItem[]>([])
  const [formOpen, setFormOpen] = useState(false)
  const [taskLists, setTaskLists] = useState<TaskList[]>([])
  const [pendingDescriptionImages, setPendingDescriptionImages] = useState<File[]>([])
  const [descriptionAttachments, setDescriptionAttachments] = useState<UploadFile[]>([])
  const [descriptionKey, setDescriptionKey] = useState(0)
  const [form] = Form.useForm<TicketFormData>()
  const selectedClientId = Form.useWatch('client_id', form)
  const selectedProjectId = Form.useWatch('project_id', form)
  const selectedRecordTypeId = Form.useWatch('record_type_id', form)
  const selectedPriority = Form.useWatch('priority', form)
  const selectedToolId = Form.useWatch('tool_id', form)
  const selectedProcessId = Form.useWatch('process_id', form)
  /** Fase 3: "Tarea" oculta la clasificación de incidente y muestra "Lista" (FR-001/002/010).
   * spec 009: el formulario reducido se mantiene (Assumptions) — solo cambia "Lista" de texto
   * libre a una entidad real (`list_id`, acotada al Proyecto elegido). */
  const isTaskSelected = recordTypes.find(rt => rt.id === selectedRecordTypeId)?.name === 'Tarea'
  // OBS-0045/0046: Proyecto/Usuario-cliente obligatorios y Cliente auto-derivado solo aplican a
  // la creación de Tickets (no Tareas) desde perfil interno — autoservicio y Tareas conservan
  // el comportamiento previo (ambos opcionales, Cliente elegido manualmente).
  const projectRequiredFlow = !isEncargado && !isTaskSelected
  const applicableSlaRule = projectSlaRules.find(r => r.priority === selectedPriority)

  // OBS-0049: Proceso sugerido (no restrictivo) según la Herramienta elegida — se agrupa en
  // "Sugeridos"/"Otros" pero cualquier combinación sigue siendo seleccionable.
  const linkedProcessIds = new Set(
    toolProcessLinks.filter(l => l.tool_id === selectedToolId).map(l => l.process_id))
  const processOptions: DefaultOptionType[] = selectedToolId && linkedProcessIds.size > 0
    ? [
        { label: 'Sugeridos', options: processes.filter(p => linkedProcessIds.has(p.id))
            .map(p => ({ value: p.id, label: p.name })) },
        { label: 'Otros', options: processes.filter(p => !linkedProcessIds.has(p.id))
            .map(p => ({ value: p.id, label: p.name })) },
      ]
    : processes.map(p => ({ value: p.id, label: p.name }))

  // OBS-0047/0048: Skills sugeridas (no impuestas) derivadas de la Herramienta y/o Proceso ya
  // elegidos en el ticket — `skill.tool_id`/`skill.process_id` ya existen en el catálogo de Skills.
  const suggestedSkillIds = new Set(
    skills.filter(s => (selectedToolId && s.tool_id === selectedToolId)
      || (selectedProcessId && s.process_id === selectedProcessId)).map(s => s.id))
  const skillOptions: DefaultOptionType[] = suggestedSkillIds.size > 0
    ? [
        { label: 'Sugeridas', options: skills.filter(s => suggestedSkillIds.has(s.id))
            .map(s => ({ value: s.id, label: `${s.code} — ${s.label}` })) },
        { label: 'Otras', options: skills.filter(s => !suggestedSkillIds.has(s.id))
            .map(s => ({ value: s.id, label: `${s.code} — ${s.label}` })) },
      ]
    : skills.map(s => ({ value: s.id, label: `${s.code} — ${s.label}` }))

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const res = await ticketService.list({
        page, page_size: 20,
        search: search || undefined,
        status: statusFilter.length ? statusFilter : undefined,
        client_id: clientFilter,
        priority: priorityFilter,
        severity: severityFilter,
        assignee_id: assigneeFilter,
        sla_status: slaStatusFilter,
        sort,
      })
      setTickets(res.items)
      setTotal(res.total)
    } finally {
      setLoading(false)
    }
  }, [page, search, statusFilter, clientFilter, priorityFilter, severityFilter, assigneeFilter, slaStatusFilter, sort])

  useEffect(() => { load() }, [load])

  const loadStats = useCallback(async () => {
    try {
      const [nuevo, enProgreso, pendienteUsuario, resuelto, vencenHoy] = await Promise.all([
        ticketService.list({ status: ['nuevo'], page_size: 1 }).then(r => r.total),
        ticketService.list({ status: IN_PROGRESS_STATUSES, page_size: 1 }).then(r => r.total),
        ticketService.list({ status: ['pendiente_usuario'], page_size: 1 }).then(r => r.total),
        ticketService.list({ status: ['resuelto'], page_size: 1 }).then(r => r.total),
        ticketService.list({ sla_expiring_within_hours: 24, page_size: 1 }).then(r => r.total),
      ])
      setStats({ nuevo, enProgreso, pendienteUsuario, resuelto, vencenHoy })
    } catch {
      message.error('No se pudieron cargar las estadísticas de tickets')
    }
  }, [])

  useEffect(() => { loadStats() }, [loadStats])

  useEffect(() => {
    if (!isEncargado) return
    // Spec 010 (FR-007): el autoservicio elige Proyecto solo entre sus vinculados
    clientContactService.myProjects().then(r => setMyProjects(r.items)).catch(() => undefined)
  }, [isEncargado])

  useEffect(() => {
    if (isEncargado) return  // sin permiso sobre clients/catalogs/resources — alta simplificada
    clientService.list({ active: true, page_size: 100 }).then(r => setClients(r.items))
      .catch(() => message.error('No se pudo cargar la lista de clientes'))
    catalogService.list('tools').then(r => setTools(r.items))
      .catch(() => message.error('No se pudo cargar el catálogo de herramientas'))
    catalogService.list('processes').then(r => setProcesses(r.items))
      .catch(() => message.error('No se pudo cargar el catálogo de procesos'))
    // OBS-0049: vínculos sugeridos Herramienta↔Proceso para guiar (no restringir) el selector.
    catalogService.listToolProcesses().then(r => setToolProcessLinks(r.items)).catch(() => undefined)
    resourceService.list({ active: true, page_size: 100 }).then(r => setResources(r.items))
      .catch(() => message.error('No se pudo cargar la lista de recursos'))
    skillService.list(true).then(r => setSkills(r.items))
      .catch(() => message.error('No se pudo cargar el catálogo de skills'))
    // Fase 3: "Ticket" y "Tarea" son ambos creables — el default al abrir el form es "Ticket"
    // (no el primero alfabético, que sería "Tarea").
    catalogService.list('record-types').then(r => {
      setRecordTypes(r.items)
      const ticketType = r.items.find(rt => rt.name === 'Ticket') ?? r.items[0]
      if (ticketType) form.setFieldValue('record_type_id', ticketType.id)
    }).catch(() => message.error('No se pudo cargar el catálogo de tipo de registro'))
  }, [form, isEncargado])

  useEffect(() => {
    if (selectedClientId) {
      projectService.list({ client_id: selectedClientId, active: true, page_size: 100 })
        .then(r => setProjects(r.items))
        .catch(() => message.error('No se pudo cargar la lista de proyectos'))
      // Cascada Cliente→Proyecto→Encargado (spec 035): al cambiar de Cliente, Proyecto y
      // Encargado ya elegidos dejan de ser válidos y se limpian.
      form.setFieldValue('project_id', undefined)
      form.setFieldValue('client_contact_id', undefined)
    } else {
      setProjects([])
      setContacts([])
    }
  }, [selectedClientId, form])

  useEffect(() => {
    if (selectedProjectId) {
      taskListService.listByProject(selectedProjectId).then(setTaskLists)
        .catch(() => message.error('No se pudo cargar la lista de Listas del proyecto'))
      // Spec 010 (US2): el solicitante se alimenta del personal del Proyecto — se limpia
      // y recarga al cambiar de proyecto.
      // Spec 034 (US1/FR-003): excluye cuentas deshabilitadas de nuevas asignaciones
      clientContactService.list({ project_id: selectedProjectId, page_size: 100, active: true })
        .then(r => setContacts(r.items))
        .catch(() => message.error('No se pudo cargar la lista de usuarios/cliente'))
      form.setFieldValue('list_id', undefined)
      form.setFieldValue('client_contact_id', undefined)
    } else {
      setTaskLists([])
      setContacts([])
      form.setFieldValue('client_contact_id', undefined)
    }
  }, [selectedProjectId, form])

  useEffect(() => {
    if (projectRequiredFlow && selectedProjectId) {
      slaService.list({ project_id: selectedProjectId, page_size: 100 })
        .then(r => setProjectSlaRules(r.items))
        .catch(() => setProjectSlaRules([]))
    } else {
      setProjectSlaRules([])
    }
  }, [projectRequiredFlow, selectedProjectId])

  const handleCreate = async (values: TicketFormData) => {
    try {
      const { skill_ids, ...ticketFields } = values
      const rawAttachments = descriptionAttachments.map(f => f.originFileObj).filter((f): f is NonNullable<typeof f> => !!f)
      const created = await ticketService.create(ticketFields, pendingDescriptionImages, rawAttachments)
      // OBS-0047/0048: solo quien tiene tickets:manage_skills fija Skills requeridas (el campo
      // ni siquiera se muestra sin el permiso, pero se guarda por si acaso cambia el rol a mitad
      // de una sesión abierta).
      if (canManageSkills && skill_ids?.length) {
        await ticketService.updateTicketSkills(created.id, skill_ids)
      }
      message.success(`Ticket ${created.ticket_number} creado`)
      setFormOpen(false)
      form.resetFields()
      setPendingDescriptionImages([]); setDescriptionAttachments([]); setDescriptionKey(k => k + 1)
      load()
      loadStats()
    } catch (err: unknown) {
      if (mapApiErrorToFormFields(err, form, TICKET_ERROR_RULES)) return
      const msg = (err as { response?: { data?: { message?: string } } }).response?.data?.message ?? 'Error al crear el ticket'
      message.error(msg)
    }
  }

  const currentCriteria: TicketFilterCriteria = {
    search: search || undefined,
    status: statusFilter.length ? statusFilter : undefined,
    client_id: clientFilter,
    priority: priorityFilter,
    severity: severityFilter,
    assignee_id: assigneeFilter,
  }

  const applySavedFilter = (criteria: TicketFilterCriteria) => {
    setSearch(criteria.search ?? '')
    setStatusFilter(criteria.status ?? [])
    setClientFilter(criteria.client_id)
    setPriorityFilter(criteria.priority)
    setSeverityFilter(criteria.severity)
    setAssigneeFilter(criteria.assignee_id)
    setPage(1)
  }

  const handleTableChange: TableProps<TicketListItem>['onChange'] = (pagination, filters) => {
    setPage(pagination.current || 1)
    setClientFilter((filters.client?.[0] as string) || undefined)
    setStatusFilter((filters.status as TicketStatus[] | null) || [])
    setPriorityFilter((filters.priority?.[0] as Priority) || undefined)
    setSeverityFilter((filters.severity?.[0] as Severity) || undefined)
    setAssigneeFilter((filters.assignee?.[0] as string) || undefined)
    setSlaStatusFilter((filters.sla?.[0] as TicketListItem['sla']['status']) || undefined)
  }

  const columns: ColumnsType<TicketListItem> = [
    { title: 'Número', dataIndex: 'ticket_number', width: 110,
      render: (v: string, t: TicketListItem) => <a className="tabular-nums" onClick={() => navigate(`/tickets/${t.id}`, {
        state: { from: { pathname: '/tickets', label: 'Tickets' } },
      })}>{v}</a> },
    {
      title: 'Tipo', dataIndex: 'record_type', key: 'record_type', width: 105,
      render: (rt: TicketListItem['record_type'], t: TicketListItem) => {
        const isSubtask = rt === 'Tarea' && !!t.parent_task_id
        const chip = rt === 'Tarea' ? vivid.purple : vivid.blue
        return (
          <span style={{
            fontSize: 11, fontWeight: 700, padding: '1px 8px', borderRadius: 999,
            background: chip.bg, color: chip.text,
          }}>
            {isSubtask ? 'Subtarea' : rt}
          </span>
        )
      },
    },
    {
      title: 'Título', dataIndex: 'title', ellipsis: true,
      ...textColumnFilter('Buscar título o número...', search, setSearch),
    },
    {
      title: 'Cliente', dataIndex: ['client', 'name'], key: 'client', width: 160, ellipsis: true,
      ...serverColumnFilter(clients.map(c => ({ text: c.name, value: c.id })), clientFilter),
    },
    {
      title: 'Estado', dataIndex: 'status', key: 'status', width: 150,
      render: (s: TicketStatus) => <TicketStatusTag status={s} />,
      filters: statusOptions.map(o => ({ text: o.label, value: o.value })),
      filteredValue: statusFilter.length ? statusFilter : null,
      onFilter: () => true,
    },
    {
      title: 'SLA', dataIndex: 'sla', key: 'sla', width: 110,
      render: (sla: TicketListItem['sla']) => <SlaStatusTag status={sla.status} />,
      ...serverColumnFilter(SLA_STATUS_OPTIONS, slaStatusFilter),
    },
    {
      title: 'Prioridad', dataIndex: 'priority', key: 'priority', width: 125,
      render: (p: Priority) => <PriorityBadge priority={p} />,
      ...serverColumnFilter(priorityOptions.map(o => ({ text: o.label, value: o.value })), priorityFilter),
    },
    {
      title: 'Severidad', dataIndex: 'severity', key: 'severity', width: 120,
      render: (s: string) => s.toUpperCase(),
      ...serverColumnFilter(severityOptions.map(o => ({ text: o.label, value: o.value })), severityFilter),
    },
    {
      title: 'Asignado', dataIndex: ['assignee', 'full_name'], key: 'assignee', width: 160,
      render: (v: string | undefined) => v ?? <em>—</em>,
      ...serverColumnFilter(resources.map(r => ({ text: r.full_name, value: r.id })), assigneeFilter),
    },
    {
      title: 'Acciones', key: 'actions', width: 110,
      render: (_: unknown, t: TicketListItem) => (
        <Space>
          <Tooltip title="Ver detalle">
            <Button size="small" icon={<EyeOutlined />} onClick={() => navigate(`/tickets/${t.id}`, {
              state: { from: { pathname: '/tickets', label: 'Tickets' } },
            })} />
          </Tooltip>
          {canAssign && (t.status === 'nuevo' || t.status === 'pre_analisis') && (
            <Tooltip title="Asignar (Triage)">
              <Button size="small" icon={<UserSwitchOutlined />} onClick={() => setAssigningId(t.id)} />
            </Tooltip>
          )}
        </Space>
      ),
    },
  ]

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 20 }}>
        <Col xs={12} md={8} lg={4}>
          <StatCard label="Nuevos" value={stats?.nuevo ?? '—'} icon={<InboxOutlined />} color="blue" sub="Pendientes de triage" />
        </Col>
        <Col xs={12} md={8} lg={4}>
          {/* OBS-0051: "En progreso" se leía como si fuera un estado real del ciclo de vida;
             "Activos" deja claro que es un agregado, el subtítulo ya lista los estados que agrupa. */}
          <StatCard label="Activos" value={stats?.enProgreso ?? '—'} icon={<ThunderboltOutlined />} color="orange" sub="Contacto → En pruebas (varios estados)" />
        </Col>
        <Col xs={12} md={8} lg={4}>
          <StatCard label="Pend. usuario" value={stats?.pendienteUsuario ?? '—'} icon={<ClockCircleOutlined />} color="magenta" sub="SLA pausado (Fase 4)" />
        </Col>
        <Col xs={12} md={8} lg={4}>
          <StatCard label="Resueltos" value={stats?.resuelto ?? '—'} icon={<CheckCircleOutlined />} color="green" sub="Pendientes de cierre" />
        </Col>
        <Col xs={12} md={8} lg={4}>
          <StatCard label="Vencen hoy" value={stats?.vencenHoy ?? '—'} icon={<FieldTimeOutlined />} color="red"
            sub="SLA vence en menos de 24h" />
        </Col>
      </Row>

      {!isEncargado && (
        <div style={{ marginBottom: 12 }}>
          <SavedFiltersBar currentCriteria={currentCriteria} onApply={applySavedFilter} />
        </div>
      )}

      <PageToolbar
        filters={isEncargado
          ? <Input.Search placeholder="Buscar por título o número..." onSearch={setSearch} allowClear style={{ width: 240 }} />
          : <>
              <Input.Search placeholder="Buscar por título o número..." onSearch={setSearch} allowClear style={{ width: 240 }} />
              <Select mode="multiple" placeholder="Estados" allowClear style={{ minWidth: 180 }}
                value={statusFilter} onChange={setStatusFilter} options={statusOptions} maxTagCount={2} />
              <Select placeholder="Cliente" allowClear showSearch optionFilterProp="label" style={{ width: 170 }}
                onChange={setClientFilter} options={clients.map(c => ({ value: c.id, label: c.name }))} />
              <Select placeholder="Prioridad" allowClear style={{ width: 120 }}
                onChange={setPriorityFilter} options={priorityOptions} />
              <Select placeholder="Asignado" allowClear showSearch optionFilterProp="label" style={{ width: 160 }}
                onChange={setAssigneeFilter} options={resources.map(r => ({ value: r.id, label: r.full_name }))} />
            </>}
        action={canCreate && (
          <Button type="primary" icon={<PlusOutlined />} onClick={() => {
            form.resetFields()
            setPendingDescriptionImages([]); setDescriptionAttachments([]); setDescriptionKey(k => k + 1)
            const ticketType = recordTypes.find(rt => rt.name === 'Ticket') ?? recordTypes[0]
            if (!isEncargado && ticketType) form.setFieldValue('record_type_id', ticketType.id)
            setFormOpen(true)
          }}>
            Nuevo ticket
          </Button>
        )}
      />

      <div style={{ marginBottom: 8 }}><SortIndicator value={sort} onChange={setSort} /></div>
      <Table rowKey="id" columns={columns} dataSource={tickets} loading={loading}
        pagination={{ current: page, total, pageSize: 20 }} onChange={handleTableChange} />

      <Modal title="Nuevo ticket" open={formOpen} onCancel={() => setFormOpen(false)}
        onOk={() => form.submit()} okText="Crear ticket" width={isEncargado ? 480 : 760}>
        <Form form={form} layout="vertical" onFinish={handleCreate}
          initialValues={isEncargado ? {} : { ticket_type: 'incident', priority: 'medium', severity: 's3', escalation_level: 'n2' }}>
          <Form.Item name="title" label="Título" rules={TITLE_RULES}>
            <Input />
          </Form.Item>
          <Form.Item name="description" label="Descripción"
            rules={[{ required: true, message: 'La descripción es requerida' },
              { validator: (_r, v) => (isRichTextEmpty(v || '') ? Promise.reject(new Error('La descripción es requerida')) : Promise.resolve()) }]}>
            <RichTextEditor key={descriptionKey} placeholder="Descripción" allowImages
              onPendingImage={file => setPendingDescriptionImages(prev => [...prev, file])} />
          </Form.Item>
          <Form.Item label="Adjuntos de la descripción">
            <Upload multiple beforeUpload={() => false} fileList={descriptionAttachments}
              onChange={({ fileList }) => setDescriptionAttachments(fileList)}>
              <Button icon={<UploadOutlined />}>Adjuntar (máx 10 MB c/u)</Button>
            </Upload>
          </Form.Item>
          {isEncargado && (
            <Form.Item name="project_id" label="Proyecto (opcional)">
              <Select allowClear disabled={myProjects.length === 0}
                placeholder={myProjects.length === 0 ? 'Sin proyectos vinculados' : 'Proyecto'}
                options={myProjects.map(p => ({ value: p.id, label: p.name }))} />
            </Form.Item>
          )}
          {!isEncargado && <>
            <Form.Item name="record_type_id" label="Tipo de registro"
              rules={[{ required: true, message: 'Selecciona el tipo de registro' }]}>
              <Segmented options={recordTypes.map(rt => ({ value: rt.id, label: rt.name }))} />
            </Form.Item>
            {/* Cascada Cliente→Proyecto→Encargado (spec 035): Cliente siempre primero; Proyecto
               se filtra por Cliente y Encargado se filtra por Proyecto, para Ticket y Tarea. */}
            <Space style={{ display: 'flex' }} align="start" wrap>
              <Form.Item name="client_id" label="Cliente" rules={[{ required: true, message: 'El cliente es requerido' }]}>
                <Select showSearch optionFilterProp="label" placeholder="Cliente" style={{ width: 220 }}
                  options={clients.map(c => ({ value: c.id, label: c.name }))} />
              </Form.Item>
              <Form.Item name="project_id" label={projectRequiredFlow ? 'Proyecto' : 'Proyecto (opcional)'}
                rules={projectRequiredFlow ? [{ required: true, message: 'El proyecto es requerido' }] : []}>
                <Select allowClear={!projectRequiredFlow} showSearch optionFilterProp="label"
                  placeholder={selectedClientId ? 'Proyecto' : 'Elige cliente primero'}
                  disabled={!selectedClientId} style={{ width: 220 }}
                  options={projects.map(p => ({ value: p.id, label: p.name }))} />
              </Form.Item>
              <Form.Item name="client_contact_id" label={projectRequiredFlow ? 'Usuario/cliente' : 'Usuario/cliente (opcional)'}
                rules={projectRequiredFlow && contacts.length > 0 ? [{ required: true, message: 'El Usuario/cliente solicitante es requerido' }] : []}>
                <Select allowClear placeholder={
                  !selectedProjectId ? 'Elige proyecto primero'
                    : contacts.length === 0 ? 'Sin personal Usuario/cliente en el proyecto' : 'Usuario/cliente'
                } disabled={!selectedProjectId || contacts.length === 0} style={{ width: 220 }}
                  options={contacts.map(c => ({ value: c.id, label: c.username }))} />
              </Form.Item>
              {isTaskSelected && (
                <Form.Item name="list_id" label="Lista (opcional)">
                  <Select allowClear placeholder={selectedProjectId ? 'Lista' : 'Elige proyecto primero'}
                    disabled={!selectedProjectId} style={{ width: 200 }}
                    options={taskLists.map(l => ({ value: l.id, label: l.name }))} />
                </Form.Item>
              )}
            </Space>
            {projectRequiredFlow && selectedProjectId && contacts.length === 0 && (
              <Alert
                type="warning" showIcon style={{ marginBottom: 12 }}
                message="Este proyecto no tiene ningún Usuario/cliente cargado"
                description='Puedes crear el ticket igual (el campo queda sin completar) — agrega un Usuario/cliente en Maestros > Usuarios/cliente para poder asociarlo la próxima vez.'
              />
            )}
            {projectRequiredFlow && selectedProjectId && (
              <Descriptions size="small" column={1} bordered style={{ marginBottom: 12 }}>
                <Descriptions.Item label="Nivel de servicio (SLA)">
                  {applicableSlaRule
                    ? `Contacto: ${applicableSlaRule.contact_minutes} min · Ejecución: ${applicableSlaRule.execution_minutes} min (prioridad ${PRIORITY_LABELS[selectedPriority as Priority] ?? selectedPriority})`
                    : 'Este proyecto/prioridad no tiene una regla de SLA configurada'}
                </Descriptions.Item>
              </Descriptions>
            )}
            <>
              <Space style={{ display: 'flex' }} align="start" wrap>
                <Form.Item name="ticket_type" label="Tipo" rules={isTaskSelected ? [] : [{ required: true }]}>
                  <Select style={{ width: 130 }} options={typeOptions} allowClear={isTaskSelected} />
                </Form.Item>
                <Form.Item name="priority" label="Prioridad" rules={isTaskSelected ? [] : [{ required: true }]}>
                  <Select style={{ width: 110 }} options={priorityOptions} allowClear={isTaskSelected} />
                </Form.Item>
                <Form.Item name="severity" label="Severidad" rules={isTaskSelected ? [] : [{ required: true }]}>
                  <Select style={{ width: 100 }} options={severityOptions} allowClear={isTaskSelected} />
                </Form.Item>
                <Form.Item name="escalation_level" label="Nivel">
                  <Select style={{ width: 90 }} allowClear={isTaskSelected}
                    options={['n1', 'n2', 'n3', 'n4'].map(v => ({ value: v, label: v.toUpperCase() }))} />
                </Form.Item>
              </Space>
              <Space style={{ display: 'flex' }} align="start">
                <Form.Item name="tool_id" label="Herramienta">
                  <Select allowClear placeholder="Herramienta" style={{ width: 200 }}
                    options={tools.map(t => ({ value: t.id, label: t.name }))} />
                </Form.Item>
                <Form.Item name="process_id" label="Proceso">
                  <Select allowClear placeholder="Proceso" style={{ width: 200 }}
                    options={processOptions} />
                </Form.Item>
              </Space>
              {/* spec 035: visible para todos los roles internos — solo Coordinador puede
                 editarla (tickets:manage_skills), el resto la ve deshabilitada. */}
              <Form.Item name="skill_ids" label="Skills requeridas (opcional)">
                <Select mode="multiple" allowClear disabled={!canManageSkills}
                  placeholder="Sin Skills requeridas" options={skillOptions} />
              </Form.Item>
            </>
          </>}
        </Form>
      </Modal>

      <AssignModal ticketId={assigningId} onClose={() => setAssigningId(null)} onAssigned={load} />
    </div>
  )
}
