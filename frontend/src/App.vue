<template>
  <div id="app">
    <AppHeader v-if="showHeader" />
    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { RouterView } from 'vue-router'
import AppHeader from '@/components/AppHeader.vue'

const route = useRoute()
const showHeader = computed(() => route.path !== '/login')
</script>

<style>
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #fafafa;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}
</style>
