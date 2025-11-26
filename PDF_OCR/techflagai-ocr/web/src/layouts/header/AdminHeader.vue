<template>
  <a-layout-header :class="[headerTheme, 'admin-header']">
    <div :class="['admin-header-wide', layout, pageWidth]">
      <router-link v-if="isMobile || layout === 'head'" to="/" :class="['logo', isMobile ? null : 'pc', headerTheme]">
        <img width="32" src="@/assets/img/logo.png" />
        <h1 v-if="!isMobile">{{systemName}}</h1>
      </router-link>
      <a-divider v-if="isMobile" type="vertical" />
      
      <div :class="['admin-header-right', headerTheme]">
          <a-tooltip class="header-item" title="帮助文档" placement="bottom" >
            <a :href="helpUrl" target="_blank">
              <a-icon type="question-circle-o" />
            </a>
          </a-tooltip>
          <header-avatar class="header-item"/>
          
      </div>
    </div>
  </a-layout-header>
</template>

<script>

import HeaderAvatar from './HeaderAvatar'
import {mapState, mapMutations} from 'vuex'

export default {
  name: 'AdminHeader',
  components: { HeaderAvatar},
  props: ['collapsed', 'menuData'],
  data() {
    return {
      
      searchActive: false,
      helpUrl: process.env.VUE_APP_WEBSITE + '/help/' // 添加这一行
    }
  },
  computed: {
    ...mapState('setting', ['theme', 'isMobile', 'layout', 'systemName', 'lang', 'pageWidth']),
    headerTheme () {
      if (this.layout == 'side' && this.theme.mode == 'dark' && !this.isMobile) {
        return 'light'
      }
      return this.theme.mode
    },
    menuWidth() {
      const {layout, searchActive} = this
      const headWidth = layout === 'head' ? '100% - 188px' : '100%'
      const extraWidth = searchActive ? '600px' : '400px'
      return `calc(${headWidth} - ${extraWidth})`
    }
  },
  methods: {
    toggleCollapse () {
      this.$emit('toggleCollapse')
    },
    onSelect (obj) {
      this.$emit('menuSelect', obj)
    },
    ...mapMutations('setting', ['setLang'])
  }
}
</script>

<style lang="less" scoped>
@import "index";
</style>
