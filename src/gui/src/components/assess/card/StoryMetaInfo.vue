<template>
  <table class="story-meta-info">
    <tr>
      <td v-if="!compactView">
        <strong>{{ t('assess.published') }}:</strong>
      </td>
      <td>
        <span :class="published_date_outdated ? 'text-error' : ''">
          {{ getPublishedDate }}
        </span>
        <v-icon
          v-if="published_date_outdated"
          class="ml-1"
          size="small"
          color="error"
          icon="mdi-alert-outline"
        />
      </td>
      <div v-if="story_in_reports > 0" class="shared-icons-container">
        <v-icon
          v-for="n in story_in_reports"
          :key="n"
          :style="getSharingIcon(n)"
          icon="mdi-share"
        />
      </div>
    </tr>

    <tr v-if="!compactView && story.tags && !reportView">
      <td>
        <strong> Tags: </strong>
      </td>
      <td>
        <tag-list
          :tags="filteredTags"
          :truncate="!detailView"
          :color="detailView"
          :editable="detailView"
          @edit="editTags()"
        />
      </td>
    </tr>

    <tr v-if="!compactView && !reportView">
      <td><strong>Relevance:</strong></td>
      <td>
        {{ story.relevance }}
      </td>
    </tr>

    <tr v-if="detailView">
      <td v-if="!compactView"><strong>Vote:</strong></td>
      <td>
        <v-list-item class="px-0">
          <story-votes :story="story" />
        </v-list-item>
      </td>
    </tr>

    <article-info
      :news-item="story.news_items[0]"
      :compact-view="compactView"
    />
    <author-info
      v-if="detailView && story.news_items.length === 1"
      :news-item="story.news_items[0]"
    />
    <v-dialog v-model="showTagDialog" width="auto">
      <popup-edit-tags
        :tags="story.tags"
        :story-id="story.id"
        @close="showTagDialog = false"
      />
    </v-dialog>
  </table>
</template>

<script>
import TagList from '@/components/assess/card/TagList.vue'
import { useFilterStore } from '@/stores/FilterStore'
import { useMainStore } from '@/stores/MainStore'
import { useI18n } from 'vue-i18n'
import { computed, ref } from 'vue'
import { useDisplay } from 'vuetify'
import { storeToRefs } from 'pinia'
import { getAssessSharingIcon } from '@/utils/helpers'
import ArticleInfo from '@/components/assess/card/ArticleInfo.vue'
import AuthorInfo from '@/components/assess/card/AuthorInfo.vue'
import PopupEditTags from '@/components/popups/PopupEditTags.vue'
import StoryVotes from '@/components/assess/card/StoryVotes.vue'

export default {
  name: 'StoryMetaInfo',
  components: {
    PopupEditTags,
    ArticleInfo,
    AuthorInfo,
    StoryVotes,
    TagList
  },
  props: {
    story: {
      type: Object,
      required: true
    },
    detailView: {
      type: Boolean,
      default: false
    },
    reportView: { type: Boolean, default: false }
  },
  setup(props) {
    const { d, t } = useI18n()
    const { name: displayName } = useDisplay()
    const { showWeekChart, compactView } = storeToRefs(useFilterStore())
    const { drawerVisible } = storeToRefs(useMainStore())

    const showTagDialog = ref(false)

    const published_dates = computed(() => {
      const pub_dates = props.story.news_items
        ? props.story.news_items.map((item) => item.published).sort()
        : []

      if (pub_dates.length === 0) {
        console.warn('No published dates found for story', props.story.title)
        return [null, null]
      }

      return [pub_dates[pub_dates.length - 1], pub_dates[0]]
    })

    const published_date_outdated = computed(() => {
      const pub_date = new Date(published_dates.value[0])
      if (!pub_date) {
        return false
      }
      const oneWeekAgo = new Date()
      oneWeekAgo.setDate(oneWeekAgo.getDate() - 6)
      return oneWeekAgo > pub_date
    })

    const tagLimit = computed(() => {
      if (props.detailView) {
        return 20
      }
      let limit = 2 // Default value
      switch (displayName.value) {
        case 'lg':
          limit = 3
          break
        case 'xl':
          limit = 4
          break
        case 'xxl':
          limit = 5
          break
        default:
          limit = 2
      }
      if (drawerVisible.value) {
        limit -= 1
      }
      return limit
    })

    const filteredTags = computed(() => {
      return [...new Set(props.story.tags.slice(0, tagLimit.value))]
    })

    const story_in_reports = computed(() => {
      return props.story ? props.story.in_reports_count : 0
    })

    const getPublishedDate = computed(() => {
      const pubDateNew = new Date(published_dates.value[0])
      const pubDateNewStr = d(pubDateNew, 'long')
      const pubDateOld = new Date(published_dates.value[1])
      const pubDateOldStr = d(pubDateOld, 'long')
      if (pubDateNew && pubDateOld) {
        return pubDateNewStr === pubDateOldStr
          ? pubDateNewStr
          : `${pubDateOldStr} - ${pubDateNewStr}`
      }
      return ''
    })

    function editTags() {
      console.log('edit tags')
      showTagDialog.value = true
    }

    function getSharingIcon(index) {
      return getAssessSharingIcon(index, story_in_reports.value)
    }

    return {
      compactView,
      showWeekChart,
      showTagDialog,
      published_dates,
      published_date_outdated,
      story_in_reports,
      getPublishedDate,
      filteredTags,
      editTags,
      getSharingIcon,
      t
    }
  }
}
</script>

<style scoped>
.detailView {
  margin-left: 120px;
  margin-right: 30px;
  padding-right: 30px;
  margin-top: 30px;
}

.story-meta-info tr td {
  vertical-align: top;
}

.story-meta-info tr td:last-child {
  width: 100%;
}

.shared-icons-container {
  position: absolute;
  margin-left: -20px;
}
</style>
