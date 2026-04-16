<template>
  <div class="relative w-full h-96 rounded-2xl overflow-hidden border border-dark-700">
    <!-- Карта -->
    <div ref="mapContainer" class="w-full h-full"></div>
    
    <!-- Информация о выбранной точке -->
    <div v-if="selectedAddress" class="absolute bottom-4 left-4 right-4 glass p-4 rounded-xl">
      <div class="flex items-start justify-between">
        <div class="flex-1">
          <p class="text-white font-medium mb-1">📍 Выбранный адрес:</p>
          <p class="text-dark-300 text-sm">{{ selectedAddress }}</p>
        </div>
        <button
          v-if="selectedAddress"
          @click="clearSelection"
          class="ml-3 w-8 h-8 glass-button rounded-full flex items-center justify-center"
        >
          <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>
    </div>
    
    <!-- Загрузка -->
    <div v-if="isLoading" class="absolute inset-0 bg-dark-900/80 backdrop-blur-sm flex items-center justify-center">
      <div class="text-center">
        <div class="w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
        <p class="text-dark-400 text-sm">Загрузка карты...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'

const props = defineProps({
  modelValue: Object, // { lat, lng, address }
  defaultAddress: String,
})

const emit = defineEmits(['update:modelValue', 'address-selected', 'update:address'])

const mapContainer = ref(null)
const isLoading = ref(true)
const selectedAddress = ref('')

let ymaps = null
let map = null
let placemark = null

// Координаты Калуги (центр)
const KALUGA_COORDS = [54.5293, 36.2754]

// Адрес пиццерии
const PIZZERIA_ADDRESS = 'Калуга, улица Кирова, 1'
const PIZZERIA_COORDS = [54.5293, 36.2754] // Нужно уточнить через геокодер

const initMap = async () => {
  isLoading.value = true
  
  try {
    // Загружаем Яндекс Карты
    await loadYandexMaps()
    
    // Создаём карту
    map = new ymaps.Map(mapContainer.value, {
      center: PIZZERIA_COORDS,
      zoom: 14,
      controls: ['zoomControl', 'geolocationControl'],
    })
    
    // Добавляем метку пиццерии
    const pizzeriaPlacemark = new ymaps.Placemark(PIZZERIA_COORDS, {
      balloonContent: '<strong>Piazza Pizza</strong><br>Калуга, ул. Кирова, 1',
      hintContent: 'Piazza Pizza',
    }, {
      preset: 'islands#redFoodIcon',
    })
    map.geoObjects.add(pizzeriaPlacemark)
    
    // Обработчик клика по карте
    map.events.add('click', async (e) => {
      const coords = e.get('coords')
      await selectPoint(coords)
    })
    
    // Если есть сохранённый адрес - ставим метку
    if (props.modelValue?.lat && props.modelValue?.lng) {
      await selectPoint([props.modelValue.lat, props.modelValue.lng])
    }
    
    isLoading.value = false
  } catch (error) {
    console.error('Ошибка при инициализации карты:', error)
    isLoading.value = false
  }
}

const loadYandexMaps = () => {
  return new Promise((resolve, reject) => {
    if (window.ymaps) {
      ymaps = window.ymaps
      resolve()
      return
    }
    
    const script = document.createElement('script')
    script.src = `https://api-maps.yandex.ru/2.1/?apikey=${import.meta.env.VITE_YANDEX_MAPS_API_KEY}&lang=ru_RU`
    script.onload = () => {
      ymaps = window.ymaps
      ymaps.ready(() => {
        resolve()
      })
    }
    script.onerror = reject
    document.head.appendChild(script)
  })
}

const selectPoint = async (coords) => {
  try {
    const fallbackAddress = `${coords[0].toFixed(6)}, ${coords[1].toFixed(6)}`

    // Удаляем старую метку
    if (placemark) {
      map.geoObjects.remove(placemark)
    }
    
    // Создаём новую метку
    placemark = new ymaps.Placemark(coords, {
      balloonContent: '<strong>Адрес доставки</strong>',
      hintContent: 'Адрес доставки',
    }, {
      preset: 'islands#blueCircleIcon',
      draggable: true,
    })
    
    // Обработчик перетаскивания метки
    placemark.events.add('dragend', async () => {
      const newCoords = placemark.geometry.getCoordinates()
      await getReverseGeocode(newCoords)
    })
    
    map.geoObjects.add(placemark)

    // Сразу обновляем форму, даже если геокодер ответит позже или с ошибкой.
    selectedAddress.value = fallbackAddress
    const fallbackValue = {
      lat: coords[0],
      lng: coords[1],
      address: fallbackAddress,
    }
    emit('update:modelValue', fallbackValue)
    emit('address-selected', fallbackValue)
    emit('update:address', fallbackAddress)
    
    // Получаем адрес по координатам
    await getReverseGeocode(coords)
  } catch (error) {
    console.error('Ошибка при выборе точки:', error)
  }
}

const getReverseGeocode = async (coords) => {
  try {
    const result = await ymaps.geocode(coords, { results: 1 })
    const firstGeoObject = result.geoObjects.get(0)
    const address =
      firstGeoObject?.getAddressLine?.() ||
      firstGeoObject?.properties?.get('text') ||
      firstGeoObject?.properties?.get('name')

    if (address) {
      selectedAddress.value = address
      
      // Отправляем данные наверх
      const value = {
        lat: coords[0],
        lng: coords[1],
        address: address,
      }
      
      emit('update:modelValue', value)
      emit('address-selected', value)
      emit('update:address', address)
    }
  } catch (error) {
    console.error('Ошибка геокодинга:', error)
  }
}

const clearSelection = () => {
  if (placemark) {
    map.geoObjects.remove(placemark)
    placemark = null
  }
  selectedAddress.value = ''
  emit('update:modelValue', null)
  emit('address-selected', null)
  emit('update:address', '')
}

// Загружаем карту при монтировании
onMounted(() => {
  initMap()
})

// Следим за изменением адреса извне
watch(() => props.defaultAddress, (newAddress) => {
  if (!newAddress) {
    return
  }

  selectedAddress.value = newAddress
})

watch(() => props.modelValue, async (newValue) => {
  if (!newValue) {
    return
  }

  if (newValue.address) {
    selectedAddress.value = newValue.address
  }

  if (map && newValue.lat && newValue.lng) {
    const currentCoords = placemark?.geometry?.getCoordinates?.()
    if (
      currentCoords &&
      Math.abs(currentCoords[0] - newValue.lat) < 0.000001 &&
      Math.abs(currentCoords[1] - newValue.lng) < 0.000001
    ) {
      return
    }
    await selectPoint([newValue.lat, newValue.lng])
  }
}, { deep: true })
</script>

<style scoped>
.ymaps-2-1-79-ground-pane {
  filter: hue-rotate(190deg) saturate(0.8) brightness(0.6);
}
</style>
