<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNotesStore } from '@/stores/notes'
import { useTagsStore } from '@/stores/tags'
import { useEditorStore } from '@/stores/editor'
import { useUiStore } from '@/stores/ui'
import { notesApi } from '@/api/notes'
import type { Tag } from '@/types/tag'
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Placeholder from '@tiptap/extension-placeholder'
import Highlight from '@tiptap/extension-highlight'
import TaskList from '@tiptap/extension-task-list'
import TaskItem from '@tiptap/extension-task-item'
import Table from '@tiptap/extension-table'
import TableRow from '@tiptap/extension-table-row'
import TableCell from '@tiptap/extension-table-cell'
import TableHeader from '@tiptap/extension-table-header'
import Link from '@tiptap/extension-link'
import Underline from '@tiptap/extension-underline'
import Image from '@tiptap/extension-image'
import TextStyle from '@tiptap/extension-text-style'
import Color from '@tiptap/extension-color'
import Typography from '@tiptap/extension-typography'
import CharacterCount from '@tiptap/extension-character-count'
import CodeBlockLowlight from '@tiptap/extension-code-block-lowlight'
import { common, createLowlight } from 'lowlight'
import { mergeAttributes } from '@tiptap/core'
import UiButton from '@/components/ui/UiButton.vue'
import client from '@/api/client'

const route = useRoute()
const router = useRouter()
const notesStore = useNotesStore()
const tagsStore = useTagsStore()
const editorStore = useEditorStore()
const ui = useUiStore()

const notebookId = route.params.notebookId as string
const noteId = route.params.noteId as string
const title = ref('')
const isLoading = ref(true)
const saveTimer = ref<ReturnType<typeof setTimeout> | null>(null)
const isUploadingImage = ref(false)
const imageInput = ref<HTMLInputElement | null>(null)

// ── Tag management ──
const noteTags = ref<Tag[]>([])
const showTagDropdown = ref(false)

const availableTags = computed(() =>
  tagsStore.tags.filter(t => !noteTags.value.some(nt => nt.id === t.id))
)

async function attachTag(tag: Tag) {
  try {
    const updated = await notesApi.attachTag(noteId, tag.id)
    noteTags.value = updated.tags || []
    showTagDropdown.value = false
  } catch {
    ui.addToast({ type: 'error', message: 'Failed to add tag' })
  }
}

async function detachTag(tag: Tag) {
  try {
    const updated = await notesApi.detachTag(noteId, tag.id)
    noteTags.value = updated.tags || []
  } catch {
    ui.addToast({ type: 'error', message: 'Failed to remove tag' })
  }
}

// Context menu state
const contextMenu = ref({
  visible: false,
  x: 0,
  y: 0,
})
const showColorSubmenu = ref(false)

// Preset colors for the color sub-menu
const presetColors = [
  '#ef4444', '#f97316', '#f59e0b', '#eab308',
  '#22c55e', '#14b8a6', '#06b6d4', '#3b82f6',
  '#6366f1', '#8b5cf6', '#a855f7', '#d946ef',
  '#ec4899', '#f43f5e', '#6b7280', '#374151',
]

// Syntax highlighting setup
const lowlight = createLowlight(common)

// Custom CodeBlock with language label
const CodeBlockWithLabel = CodeBlockLowlight.extend({
  renderHTML({ node, HTMLAttributes }) {
    const language = node.attrs.language
    return [
      'pre',
      mergeAttributes(
        this.options.HTMLAttributes,
        HTMLAttributes,
        language ? { 'data-language': language } : {},
      ),
      [
        'code',
        {
          class: language
            ? this.options.languageClassPrefix + language
            : null,
        },
        0,
      ],
    ]
  },
}).configure({ lowlight })

const editor = useEditor({
  extensions: [
    StarterKit.configure({
      heading: { levels: [1, 2, 3] },
      codeBlock: false,
    }),
    CodeBlockWithLabel,
    Placeholder.configure({ placeholder: 'Start writing...' }),
    TextStyle,
    Color,
    Highlight,
    TaskList,
    TaskItem.configure({ nested: true }),
    Table.configure({ resizable: true }),
    TableRow,
    TableCell,
    TableHeader,
    Image.configure({
      inline: false,
      allowBase64: false,
    }),
    Link.configure({ openOnClick: false }),
    Underline,
    Typography,
    CharacterCount,
  ],
  onUpdate: () => {
    editorStore.markDirty()
    scheduleAutoSave()
  },
  editorProps: {
    attributes: {
      class: 'prose prose-sm dark:prose-invert max-w-none focus:outline-none min-h-[60vh] px-8 py-6',
    },
  },
})

function scheduleAutoSave() {
  if (saveTimer.value) clearTimeout(saveTimer.value)
  saveTimer.value = setTimeout(() => saveNote(), 3000)
}

async function saveNote() {
  if (!editor.value) return
  editorStore.setSaving(true)
  try {
    const content = editor.value.getJSON()
    await notesStore.updateNote(noteId, {
      title: title.value,
      content,
    })
    editorStore.markClean()
  } catch {
    ui.addToast({ type: 'error', message: 'Failed to save' })
  } finally {
    editorStore.setSaving(false)
  }
}

async function saveAndClose() {
  await saveNote()
  if (!editorStore.isDirty) {
    router.push({ name: 'notebook-detail', params: { id: notebookId } })
  }
}

// Get current text color for the color button indicator
function getCurrentColor(): string {
  if (!editor.value) return '#374151'
  const { from, to } = editor.value.state.selection
  if (from === to) return '#374151'
  const attrs = editor.value.getAttributes('textStyle')
  return attrs.color || '#374151'
}

function setColor(color: string) {
  if (color === '') {
    editor.value?.chain().focus().unsetColor().run()
  } else {
    editor.value?.chain().focus().setColor(color).run()
  }
}

function triggerColorPicker() {
  const input = document.getElementById('text-color-input') as HTMLInputElement | null
  input?.click()
}

// Image upload handler
function triggerImageUpload() {
  imageInput.value?.click()
}

async function handleImageUpload(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file || !editor.value) return

  // Validate file type
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml']
  if (!allowedTypes.includes(file.type)) {
    ui.addToast({ type: 'error', message: 'Unsupported image format. Use JPEG, PNG, GIF, WebP, or SVG.' })
    return
  }

  // Validate file size (5 MB)
  if (file.size > 5 * 1024 * 1024) {
    ui.addToast({ type: 'error', message: 'Image too large. Maximum size is 5 MB.' })
    return
  }

  isUploadingImage.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)

    const { data } = await client.post('/uploads/images', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 30000,
    })

    // Insert image at cursor position
    editor.value.chain().focus().setImage({ src: data.url, alt: file.name }).run()
    ui.addToast({ type: 'success', message: 'Image uploaded' })
  } catch (err: any) {
    const detail = err.response?.data?.detail || 'Failed to upload image'
    ui.addToast({ type: 'error', message: detail })
  } finally {
    isUploadingImage.value = false
    // Reset file input
    if (target) target.value = ''
  }
}

// Context menu handlers
function handleContextMenu(e: MouseEvent) {
  e.preventDefault()
  // Adjust position so the menu doesn't overflow the viewport
  const menuWidth = 210
  const menuHeight = 340
  let x = e.clientX
  let y = e.clientY
  if (x + menuWidth > window.innerWidth) {
    x = window.innerWidth - menuWidth - 8
  }
  if (y + menuHeight > window.innerHeight) {
    y = window.innerHeight - menuHeight - 8
  }
  contextMenu.value = { visible: true, x, y }
}

function closeContextMenu() {
  contextMenu.value.visible = false
  showColorSubmenu.value = false
}

function contextAction(action: string, payload?: any) {
  if (!editor.value) return
  const chain = editor.value.chain().focus()
  switch (action) {
    case 'bold': chain.toggleBold().run(); break
    case 'italic': chain.toggleItalic().run(); break
    case 'underline': chain.toggleUnderline().run(); break
    case 'highlight': chain.toggleHighlight().run(); break
    case 'heading1': chain.toggleHeading({ level: 1 }).run(); break
    case 'heading2': chain.toggleHeading({ level: 2 }).run(); break
    case 'heading3': chain.toggleHeading({ level: 3 }).run(); break
    case 'bulletList': chain.toggleBulletList().run(); break
    case 'orderedList': chain.toggleOrderedList().run(); break
    case 'taskList': chain.toggleTaskList().run(); break
    case 'blockquote': chain.toggleBlockquote().run(); break
    case 'codeBlock': chain.toggleCodeBlock().run(); break
    case 'horizontalRule': chain.setHorizontalRule().run(); break
    case 'link': {
      const url = prompt('Enter link URL:')
      if (url) {
        chain.extendMarkRange('link').setLink({ href: url }).run()
      }
      break
    }
    case 'image':
      triggerImageUpload()
      break
    case 'clearFormat':
      chain.clearNodes().unsetAllMarks().run()
      break
  }
  closeContextMenu()
}

// Close context menu on click outside or Escape
function onDocumentClick(e: MouseEvent) {
  if (contextMenu.value.visible) {
    closeContextMenu()
  }
}

// Load note
onMounted(async () => {
  try {
    const note = await notesStore.fetchNote(noteId)
    title.value = note.title
    noteTags.value = note.tags || []
    editorStore.currentNoteId = noteId
    if (note.content && editor.value) {
      editor.value.commands.setContent(note.content)
    }
    editorStore.markClean()
  } catch {
    ui.addToast({ type: 'error', message: 'Note not found' })
    router.push({ name: 'notebook-detail', params: { id: notebookId } })
  } finally {
    isLoading.value = false
  }
  // Fetch available tags
  tagsStore.fetchTags()
})

// Keyboard shortcut
function handleKeydown(e: KeyboardEvent) {
  if ((e.metaKey || e.ctrlKey) && e.key === 's') {
    e.preventDefault()
    saveNote()
  }
  if (e.key === 'Escape' && contextMenu.value.visible) {
    closeContextMenu()
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
  document.addEventListener('click', onDocumentClick)
})

onBeforeUnmount(() => {
  document.removeEventListener('keydown', handleKeydown)
  document.removeEventListener('click', onDocumentClick)
  if (saveTimer.value) clearTimeout(saveTimer.value)
  // Save on unmount if dirty
  if (editorStore.isDirty) saveNote()
})

// Auto-save on title change
watch(title, () => {
  editorStore.markDirty()
  scheduleAutoSave()
})
</script>

<template>
  <div v-if="isLoading" class="flex items-center justify-center py-32">
    <span class="i-ph-circle-notch animate-spin w-8 h-8 text-brand-500" />
  </div>

  <div v-else class="max-w-4xl mx-auto">
    <!-- Toolbar -->
    <div class="flex items-center gap-1 mb-4 p-2 glass rounded-xl border border-gray-200/50 dark:border-gray-800/50 overflow-x-auto sticky top-16 z-10">
      <button
        class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        title="Bold (Cmd+B)"
        @click="editor?.chain().focus().toggleBold().run()"
        :class="{ 'bg-brand-100 dark:bg-brand-900/30 text-brand-600': editor?.isActive('bold') }"
      >
        <span class="i-ph-text-bolder w-5 h-5" />
      </button>
      <button
        class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        title="Italic (Cmd+I)"
        @click="editor?.chain().focus().toggleItalic().run()"
        :class="{ 'bg-brand-100 dark:bg-brand-900/30 text-brand-600': editor?.isActive('italic') }"
      >
        <span class="i-ph-text-italic w-5 h-5" />
      </button>
      <button
        class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        title="Underline (Cmd+U)"
        @click="editor?.chain().focus().toggleUnderline().run()"
        :class="{ 'bg-brand-100 dark:bg-brand-900/30 text-brand-600': editor?.isActive('underline') }"
      >
        <span class="i-ph-text-underline w-5 h-5" />
      </button>
      <button
        class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        title="Highlight"
        @click="editor?.chain().focus().toggleHighlight().run()"
        :class="{ 'bg-brand-100 dark:bg-brand-900/30 text-brand-600': editor?.isActive('highlight') }"
      >
        <span class="text-sm font-bold">H</span>
      </button>

      <!-- Text color button -->
      <div class="relative" title="Text Color">
        <button
          class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          :class="{ 'bg-brand-100 dark:bg-brand-900/30 text-brand-600': !!editor?.getAttributes('textStyle').color }"
          @click="triggerColorPicker"
        >
          <span class="relative">
            <span class="i-ph-text-aa w-5 h-5" />
            <span
              class="absolute bottom-0 left-1/2 -translate-x-1/2 w-4 h-0.5 rounded-full"
              :style="{ backgroundColor: getCurrentColor() }"
            />
          </span>
        </button>
        <input
          id="text-color-input"
          type="color"
          class="sr-only"
          :value="getCurrentColor()"
          @input="setColor(($event.target as HTMLInputElement).value)"
        />
      </div>

      <div class="w-px h-6 bg-gray-200 dark:bg-gray-700 mx-1" />

      <button
        class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        title="Heading 1"
        @click="editor?.chain().focus().toggleHeading({ level: 1 }).run()"
        :class="{ 'bg-brand-100 dark:bg-brand-900/30 text-brand-600': editor?.isActive('heading', { level: 1 }) }"
      >
        <span class="text-sm font-bold">H1</span>
      </button>
      <button
        class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        title="Heading 2"
        @click="editor?.chain().focus().toggleHeading({ level: 2 }).run()"
        :class="{ 'bg-brand-100 dark:bg-brand-900/30 text-brand-600': editor?.isActive('heading', { level: 2 }) }"
      >
        <span class="text-sm font-bold">H2</span>
      </button>
      <button
        class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        title="Heading 3"
        @click="editor?.chain().focus().toggleHeading({ level: 3 }).run()"
        :class="{ 'bg-brand-100 dark:bg-brand-900/30 text-brand-600': editor?.isActive('heading', { level: 3 }) }"
      >
        <span class="text-sm font-bold">H3</span>
      </button>

      <div class="w-px h-6 bg-gray-200 dark:bg-gray-700 mx-1" />

      <button
        class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        title="Bullet List"
        @click="editor?.chain().focus().toggleBulletList().run()"
        :class="{ 'bg-brand-100 dark:bg-brand-900/30 text-brand-600': editor?.isActive('bulletList') }"
      >
        <span class="i-ph-list-bullets w-5 h-5" />
      </button>
      <button
        class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        title="Ordered List"
        @click="editor?.chain().focus().toggleOrderedList().run()"
        :class="{ 'bg-brand-100 dark:bg-brand-900/30 text-brand-600': editor?.isActive('orderedList') }"
      >
        <span class="i-ph-list-numbers w-5 h-5" />
      </button>
      <button
        class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        title="Task List"
        @click="editor?.chain().focus().toggleTaskList().run()"
        :class="{ 'bg-brand-100 dark:bg-brand-900/30 text-brand-600': editor?.isActive('taskList') }"
      >
        <span class="i-ph-check-square w-5 h-5" />
      </button>

      <div class="w-px h-6 bg-gray-200 dark:bg-gray-700 mx-1" />

      <button
        class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        title="Blockquote"
        @click="editor?.chain().focus().toggleBlockquote().run()"
        :class="{ 'bg-brand-100 dark:bg-brand-900/30 text-brand-600': editor?.isActive('blockquote') }"
      >
        <span class="i-ph-quotes w-5 h-5" />
      </button>
      <button
        class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        title="Code Block"
        @click="editor?.chain().focus().toggleCodeBlock().run()"
        :class="{ 'bg-brand-100 dark:bg-brand-900/30 text-brand-600': editor?.isActive('codeBlock') }"
      >
        <span class="i-ph-code w-5 h-5" />
      </button>
      <button
        class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        title="Horizontal Rule"
        @click="editor?.chain().focus().setHorizontalRule().run()"
      >
        <span class="i-ph-minus w-5 h-5" />
      </button>

      <div class="w-px h-6 bg-gray-200 dark:bg-gray-700 mx-1" />

      <button
        class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        title="Insert Image"
        :disabled="isUploadingImage"
        @click="triggerImageUpload"
      >
        <span v-if="isUploadingImage" class="i-ph-circle-notch animate-spin w-5 h-5" />
        <span v-else class="i-ph-image w-5 h-5" />
      </button>
      <input
        ref="imageInput"
        type="file"
        accept="image/jpeg,image/png,image/gif,image/webp,image/svg+xml"
        class="hidden"
        @change="handleImageUpload"
      />

      <div class="flex-1" />

      <button
        class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        title="Undo"
        @click="editor?.chain().focus().undo().run()"
      >
        <span class="i-ph-arrow-counter-clockwise w-5 h-5" />
      </button>
      <button
        class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        title="Redo"
        @click="editor?.chain().focus().redo().run()"
      >
        <span class="i-ph-arrow-clockwise w-5 h-5" />
      </button>
    </div>

    <!-- Title -->
    <input
      v-model="title"
      type="text"
      placeholder="Note title..."
      class="w-full text-3xl font-bold bg-transparent border-none outline-none placeholder:text-gray-300 dark:placeholder:text-gray-700 mb-3 px-8"
    />

    <!-- Tag bar -->
    <div class="flex items-center gap-2 px-8 mb-4 flex-wrap">
      <!-- Current tags -->
      <span
        v-for="tag in noteTags"
        :key="tag.id"
        class="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium transition-colors"
        :style="{ backgroundColor: tag.color + '20', color: tag.color }"
      >
        {{ tag.name }}
        <button
          class="w-4 h-4 flex items-center justify-center rounded-full hover:bg-black/10 dark:hover:bg-white/10 transition-colors"
          @click="detachTag(tag)"
          title="Remove tag"
        >
          <span class="i-ph-x w-3 h-3" />
        </button>
      </span>

      <!-- Add tag button + dropdown -->
      <div class="relative">
        <button
          class="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium text-gray-500 hover:text-brand-500 bg-gray-100 dark:bg-gray-800 hover:bg-brand-50 dark:hover:bg-brand-900/30 transition-colors"
          :class="{ 'text-brand-500 bg-brand-50 dark:bg-brand-900/30': showTagDropdown }"
          @click="showTagDropdown = !showTagDropdown"
        >
          <span class="i-ph-plus w-3.5 h-3.5" />
          Tag
        </button>

        <!-- Dropdown -->
        <div
          v-if="showTagDropdown"
          class="absolute left-0 top-full mt-1 w-52 py-1 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 shadow-lg z-40 max-h-48 overflow-y-auto"
          @click.stop
        >
          <div v-if="availableTags.length === 0" class="px-3 py-2 text-xs text-gray-400">
            No more tags available
          </div>
          <button
            v-for="tag in availableTags"
            :key="tag.id"
            class="w-full flex items-center gap-2 px-3 py-2 text-sm text-left hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
            @click="attachTag(tag)"
          >
            <span class="w-2.5 h-2.5 rounded-full flex-shrink-0" :style="{ backgroundColor: tag.color }" />
            <span class="text-gray-700 dark:text-gray-300 truncate">{{ tag.name }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Click-outside to close tag dropdown -->
    <div v-if="showTagDropdown" class="fixed inset-0 z-30" @click="showTagDropdown = false" />

    <!-- Editor -->
    <div class="glass-card overflow-hidden" @contextmenu="handleContextMenu">
      <EditorContent :editor="editor" />
    </div>

    <!-- Context Menu -->
    <Teleport to="body">
      <div
        v-if="contextMenu.visible"
        class="fixed z-50 min-w-[200px] py-1.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-white/95 dark:bg-gray-900/95 backdrop-blur-md shadow-lg shadow-black/10"
        :style="{ left: contextMenu.x + 'px', top: contextMenu.y + 'px' }"
        @click.stop
      >
        <!-- Text formatting -->
        <div class="flex items-center gap-0.5 px-2 pb-1.5 mb-1 border-b border-gray-100 dark:border-gray-800">
          <button class="context-menu-btn" :class="{ active: editor?.isActive('bold') }" title="Bold" @click="contextAction('bold')">
            <span class="i-ph-text-bolder w-4 h-4" />
          </button>
          <button class="context-menu-btn" :class="{ active: editor?.isActive('italic') }" title="Italic" @click="contextAction('italic')">
            <span class="i-ph-text-italic w-4 h-4" />
          </button>
          <button class="context-menu-btn" :class="{ active: editor?.isActive('underline') }" title="Underline" @click="contextAction('underline')">
            <span class="i-ph-text-underline w-4 h-4" />
          </button>
          <button class="context-menu-btn" :class="{ active: editor?.isActive('highlight') }" title="Highlight" @click="contextAction('highlight')">
            <span class="text-xs font-bold">H</span>
          </button>
          <div class="relative">
            <button
              class="context-menu-btn"
              :class="{ active: showColorSubmenu || !!editor?.getAttributes('textStyle').color }"
              title="Text Color"
              @click="showColorSubmenu = !showColorSubmenu"
            >
              <span class="relative">
                <span class="i-ph-text-aa w-4 h-4" />
                <span class="absolute bottom-0 left-1/2 -translate-x-1/2 w-3 h-0.5 rounded-full" :style="{ backgroundColor: getCurrentColor() }" />
              </span>
            </button>
            <!-- Color sub-menu -->
            <div
              v-if="showColorSubmenu"
              class="absolute left-0 top-full mt-1 p-2 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 shadow-lg z-50"
              style="display: flex; flex-wrap: wrap; gap: 6px; width: 122px;"
              @click.stop
            >
              <button
                v-for="c in presetColors"
                :key="c"
                class="rounded-sm border transition-colors shrink-0"
                :class="{ 'border-brand-500 !border-2': getCurrentColor() === c, 'border-gray-200/60 dark:border-gray-700/60': getCurrentColor() !== c }"
                :style="{ backgroundColor: c, width: '22px', height: '22px' }"
                :title="c"
                @click="setColor(c); showColorSubmenu = false"
              />
              <button
                class="rounded-sm border border-gray-300 dark:border-gray-600 flex items-center justify-center transition-colors hover:border-gray-400 dark:hover:border-gray-500 shrink-0"
                style="width: 22px; height: 22px;"
                title="Default"
                @click="setColor(''); showColorSubmenu = false"
              >
                <span class="i-ph-x text-gray-400" style="width: 10px; height: 10px;" />
              </button>
            </div>
          </div>
        </div>

        <!-- Headings -->
        <div class="flex items-center gap-0.5 px-2 pb-1.5 mb-1 border-b border-gray-100 dark:border-gray-800">
          <button class="context-menu-btn text-xs font-bold w-8" :class="{ active: editor?.isActive('heading', { level: 1 }) }" title="Heading 1" @click="contextAction('heading1')">H1</button>
          <button class="context-menu-btn text-xs font-bold w-8" :class="{ active: editor?.isActive('heading', { level: 2 }) }" title="Heading 2" @click="contextAction('heading2')">H2</button>
          <button class="context-menu-btn text-xs font-bold w-8" :class="{ active: editor?.isActive('heading', { level: 3 }) }" title="Heading 3" @click="contextAction('heading3')">H3</button>
        </div>

        <!-- Lists -->
        <div class="flex items-center gap-0.5 px-2 pb-1.5 mb-1 border-b border-gray-100 dark:border-gray-800">
          <button class="context-menu-btn" :class="{ active: editor?.isActive('bulletList') }" title="Bullet List" @click="contextAction('bulletList')">
            <span class="i-ph-list-bullets w-4 h-4" />
          </button>
          <button class="context-menu-btn" :class="{ active: editor?.isActive('orderedList') }" title="Ordered List" @click="contextAction('orderedList')">
            <span class="i-ph-list-numbers w-4 h-4" />
          </button>
          <button class="context-menu-btn" :class="{ active: editor?.isActive('taskList') }" title="Task List" @click="contextAction('taskList')">
            <span class="i-ph-check-square w-4 h-4" />
          </button>
        </div>

        <!-- Block -->
        <div class="flex items-center gap-0.5 px-2 pb-1.5 mb-1 border-b border-gray-100 dark:border-gray-800">
          <button class="context-menu-btn" :class="{ active: editor?.isActive('blockquote') }" title="Blockquote" @click="contextAction('blockquote')">
            <span class="i-ph-quotes w-4 h-4" />
          </button>
          <button class="context-menu-btn" :class="{ active: editor?.isActive('codeBlock') }" title="Code Block" @click="contextAction('codeBlock')">
            <span class="i-ph-code w-4 h-4" />
          </button>
          <button class="context-menu-btn" title="Horizontal Rule" @click="contextAction('horizontalRule')">
            <span class="i-ph-minus w-4 h-4" />
          </button>
        </div>

        <!-- Actions -->
        <div class="flex items-center gap-0.5 px-2 pb-1.5 mb-1 border-b border-gray-100 dark:border-gray-800">
          <button class="context-menu-btn" :class="{ active: editor?.isActive('link') }" title="Add Link" @click="contextAction('link')">
            <span class="i-ph-link w-4 h-4" />
          </button>
          <button class="context-menu-btn" title="Insert Image" @click="contextAction('image')">
            <span class="i-ph-image w-4 h-4" />
          </button>
        </div>

        <!-- Clear formatting -->
        <div class="px-2 pt-0.5">
          <button class="w-full text-left px-2 py-1 text-xs text-gray-500 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-950/20 rounded-lg transition-colors" @click="contextAction('clearFormat')">
            Clear formatting
          </button>
        </div>
      </div>
    </Teleport>

    <!-- Status bar -->
    <div class="flex items-center justify-between mt-4 px-2 text-xs text-gray-400">
      <div class="flex items-center gap-3">
        <span v-if="editorStore.isSaving" class="flex items-center gap-1.5">
          <span class="w-2 h-2 rounded-full bg-amber-400 pulse-dot" />
          Saving...
        </span>
        <span v-else-if="editorStore.isDirty" class="flex items-center gap-1.5">
          <span class="w-2 h-2 rounded-full bg-amber-400" />
          Unsaved changes
        </span>
        <span v-else class="flex items-center gap-1.5">
          <span class="w-2 h-2 rounded-full bg-emerald-400" />
          Saved
        </span>
      </div>
      <div class="flex items-center gap-4">
        <span>{{ editor?.storage.characterCount?.characters() || 0 }} chars</span>
        <span>{{ editor?.storage.characterCount?.words() || 0 }} words</span>
        <UiButton variant="ghost" size="sm" @click="saveAndClose">
          <span class="i-ph-check w-4 h-4" />
          Done
        </UiButton>
      </div>
    </div>
  </div>
</template>

<style>
/* Context menu button styles — unscoped so they work inside Teleport */
.context-menu-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  color: #6b7280;
  transition: all 0.15s ease;
  border: none;
  background: transparent;
  cursor: pointer;
}
.context-menu-btn:hover {
  background: #f3f4f6;
  color: #4f46e5;
}
.dark .context-menu-btn:hover {
  background: #1f2937;
  color: #818cf8;
}
.context-menu-btn.active {
  background: #eef2ff;
  color: #4f46e5;
}
.dark .context-menu-btn.active {
  background: #312e81;
  color: #a5b4fc;
}

/* Horizontal Rule in editor — make it clearly visible */
.ProseMirror hr {
  border: none;
  height: 2px;
  margin: 1.5rem 0;
  background: linear-gradient(
    to right,
    transparent 0%,
    #d1d5db 15%,
    #9ca3af 50%,
    #d1d5db 85%,
    transparent 100%
  );
  border-radius: 1px;
}
.dark .ProseMirror hr {
  background: linear-gradient(
    to right,
    transparent 0%,
    #4b5563 15%,
    #6b7280 50%,
    #4b5563 85%,
    transparent 100%
  );
}

/* Ensure hr is selectable for deletion */
.ProseMirror hr.ProseMirror-selectednode {
  outline: 2px solid var(--color-brand-500);
  outline-offset: 1px;
}

/* ── Task List ── */
.ProseMirror ul[data-type="taskList"] {
  list-style: none !important;
  padding-left: 0 !important;
}
/* TaskItem NodeView doesn't set data-type on <li>, only data-checked */
.ProseMirror ul[data-type="taskList"] > li {
  display: flex !important;
  align-items: flex-start;
  gap: 0.5rem;
}
.ProseMirror ul[data-type="taskList"] > li::before {
  display: none !important;
}
.ProseMirror ul[data-type="taskList"] > li > label {
  flex-shrink: 0;
  margin-top: 0.1rem;
  user-select: none;
}
.ProseMirror ul[data-type="taskList"] > li > div {
  flex: 1;
  min-width: 0;
}
.ProseMirror ul[data-type="taskList"] > li::marker {
  content: none;
}
.ProseMirror ul[data-type="taskList"] > li > div > p {
  margin-top: 0;
  margin-bottom: 0;
}

/* ── Code block: language label ── */
.ProseMirror pre {
  position: relative;
  padding-top: 2rem;
}
.ProseMirror pre[data-language]::before {
  content: attr(data-language);
  position: absolute;
  top: 0;
  left: 0.75rem;
  font-size: 0.65rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #6366f1;
  background: #eef2ff;
  padding: 0.15rem 0.5rem;
  border-radius: 0 0 4px 4px;
  pointer-events: none;
}
.dark .ProseMirror pre[data-language]::before {
  color: #a5b4fc;
  background: #312e81;
}

/* ── Syntax highlighting theme (light) ── */
.ProseMirror .hljs-comment,
.ProseMirror .hljs-quote {
  color: #6b7280;
  font-style: italic;
}
.ProseMirror .hljs-keyword,
.ProseMirror .hljs-selector-tag,
.ProseMirror .hljs-type {
  color: #a855f7;
  font-weight: 500;
}
.ProseMirror .hljs-string,
.ProseMirror .hljs-addition {
  color: #16a34a;
}
.ProseMirror .hljs-number,
.ProseMirror .hljs-literal {
  color: #ea580c;
}
.ProseMirror .hljs-title,
.ProseMirror .hljs-section,
.ProseMirror .hljs-name {
  color: #2563eb;
}
.ProseMirror .hljs-attr,
.ProseMirror .hljs-attribute {
  color: #ca8a04;
}
.ProseMirror .hljs-built_in,
.ProseMirror .hljs-function .hljs-title {
  color: #7c3aed;
}
.ProseMirror .hljs-variable,
.ProseMirror .hljs-template-variable {
  color: #dc2626;
}
.ProseMirror .hljs-regexp,
.ProseMirror .hljs-link {
  color: #0891b2;
}
.ProseMirror .hljs-tag,
.ProseMirror .hljs-selector-class {
  color: #db2777;
}
.ProseMirror .hljs-symbol,
.ProseMirror .hljs-bullet,
.ProseMirror .hljs-meta {
  color: #4f46e5;
}
.ProseMirror .hljs-deletion {
  color: #dc2626;
}
.ProseMirror .hljs-emphasis {
  font-style: italic;
}
.ProseMirror .hljs-strong {
  font-weight: 600;
}
.ProseMirror pre code .hljs-params {
  color: #374151;
}

/* ── Syntax highlighting theme (dark) ── */
.dark .ProseMirror .hljs-comment,
.dark .ProseMirror .hljs-quote {
  color: #6b7280;
}
.dark .ProseMirror .hljs-keyword,
.dark .ProseMirror .hljs-selector-tag,
.dark .ProseMirror .hljs-type {
  color: #c084fc;
}
.dark .ProseMirror .hljs-string,
.dark .ProseMirror .hljs-addition {
  color: #4ade80;
}
.dark .ProseMirror .hljs-number,
.dark .ProseMirror .hljs-literal {
  color: #fb923c;
}
.dark .ProseMirror .hljs-title,
.dark .ProseMirror .hljs-section,
.dark .ProseMirror .hljs-name {
  color: #60a5fa;
}
.dark .ProseMirror .hljs-attr,
.dark .ProseMirror .hljs-attribute {
  color: #facc15;
}
.dark .ProseMirror .hljs-built_in,
.dark .ProseMirror .hljs-function .hljs-title {
  color: #a78bfa;
}
.dark .ProseMirror .hljs-variable,
.dark .ProseMirror .hljs-template-variable {
  color: #f87171;
}
.dark .ProseMirror .hljs-regexp,
.dark .ProseMirror .hljs-link {
  color: #22d3ee;
}
.dark .ProseMirror .hljs-tag,
.dark .ProseMirror .hljs-selector-class {
  color: #f472b6;
}
.dark .ProseMirror .hljs-symbol,
.dark .ProseMirror .hljs-bullet,
.dark .ProseMirror .hljs-meta {
  color: #818cf8;
}
.dark .ProseMirror .hljs-deletion {
  color: #f87171;
}
.dark .ProseMirror pre code .hljs-params {
  color: #d1d5db;
}
</style>
