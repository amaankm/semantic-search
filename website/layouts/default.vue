<template>
  <div>
    <nav
      class="bg-slate-900/95 backdrop-blur-sm border-b border-slate-800 sticky w-full top-0 z-50 px-10"
    >
      <div class="flex items-center justify-between h-16">
        <!-- Logo/Home Link -->
        <NuxtLink
          to="/"
          class="flex items-center space-x-2 text-white hover:text-blue-400 transition-colors"
        >
          <span class="text-2xl">🔍</span>
          <span class="font-bold text-lg">SemanticSearch</span>
        </NuxtLink>

        <!-- Navigation Links -->
        <div class="flex space-x-8">
          <NuxtLink
            to="/patents"
            class="text-slate-300 hover:text-white transition-colors"
          >
            Patents
          </NuxtLink>
          <NuxtLink
            to="/papers"
            class="text-slate-300 hover:text-white transition-colors"
          >
            Papers
          </NuxtLink>
        </div>
      </div>
    </nav>
    <!-- <slot /> -->
  </div>
</template>
