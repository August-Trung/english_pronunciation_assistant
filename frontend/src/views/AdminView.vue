<template>
  <v-container fluid class="pa-4 pa-md-6">
    <!-- Admin Header Banner -->
    <v-card border flat class="pa-4 mb-4 bg-gradient-dark text-white rounded-lg elevation-2">
      <div class="d-flex align-center justify-space-between flex-wrap ga-3">
        <div class="d-flex align-center ga-3">
          <v-avatar color="white" size="48" class="elevation-2">
            <v-icon color="grey-darken-4" size="large">mdi-shield-crown-outline</v-icon>
          </v-avatar>
          <div>
            <div class="text-h6 font-weight-black tracking-tight">CỔNG QUẢN TRỊ VIÊN HỆ THỐNG (ADMIN CONSOLE)</div>
            <div class="text-caption opacity-90 font-weight-medium">
              Quản lý Đa Trường Học (Tenants), Cấp tài khoản Giảng viên, Hạn mức Seat License & Auto-Cleanup Supabase
            </div>
          </div>
        </div>

        <div class="d-flex align-center ga-2">
          <v-chip color="amber" variant="flat" class="font-weight-black text-black">
            Role: {{ activeUserRole.toUpperCase() }}
          </v-chip>
        </div>
      </div>
    </v-card>

    <!-- Super Admin KPI Metrics -->
    <v-row class="mb-4" density="comfortable">
      <v-col cols="12" sm="3">
        <v-card border flat class="pa-3 bg-white rounded-lg d-flex align-center ga-3">
          <v-avatar color="indigo-lighten-5" size="42" class="text-indigo">
            <v-icon size="default">mdi-domain</v-icon>
          </v-avatar>
          <div>
            <div class="text-caption font-weight-bold text-grey">Tổng Trường Học / Chi Nhánh</div>
            <div class="text-h6 font-weight-black text-secondary">{{ overview.total_tenants }}</div>
          </div>
        </v-card>
      </v-col>
      <v-col cols="12" sm="3">
        <v-card border flat class="pa-3 bg-white rounded-lg d-flex align-center ga-3">
          <v-avatar color="teal-lighten-5" size="42" class="text-teal-darken-3">
            <v-icon size="default">mdi-account-tie</v-icon>
          </v-avatar>
          <div>
            <div class="text-caption font-weight-bold text-grey">Tổng Số Giảng Viên</div>
            <div class="text-h6 font-weight-black text-teal-darken-3">{{ overview.total_teachers }}</div>
          </div>
        </v-card>
      </v-col>
      <v-col cols="12" sm="3">
        <v-card border flat class="pa-3 bg-white rounded-lg d-flex align-center ga-3">
          <v-avatar color="purple-lighten-5" size="42" class="text-purple-darken-3">
            <v-icon size="default">mdi-account-school-outline</v-icon>
          </v-avatar>
          <div>
            <div class="text-caption font-weight-bold text-grey">Tổng Học Sinh Active</div>
            <div class="text-h6 font-weight-black text-purple-darken-3">{{ overview.total_students }}</div>
          </div>
        </v-card>
      </v-col>
      <v-col cols="12" sm="3">
        <v-card border flat class="pa-3 bg-white rounded-lg d-flex align-center ga-3">
          <v-avatar color="blue-lighten-5" size="42" class="text-blue-darken-3">
            <v-icon size="default">mdi-cloud-outline</v-icon>
          </v-avatar>
          <div>
            <div class="text-caption font-weight-bold text-grey">Dung Lượng Supabase (0đ)</div>
            <div class="text-h6 font-weight-black text-blue-darken-3">
              {{ overview.supabase_storage_used_mb }} MB / {{ overview.supabase_storage_limit_mb }} MB
            </div>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Main Admin Workspace -->
    <v-card border flat class="pa-4 bg-white rounded-lg">
      <v-tabs v-model="activeTab" color="primary" density="compact" class="mb-4">
        <v-tab value="tenants" class="font-weight-black text-none" prepend-icon="mdi-domain">
          Quản Lý Trường Học (Tenants)
        </v-tab>
        <v-tab value="provision" class="font-weight-black text-none" prepend-icon="mdi-account-plus-outline">
          Cấp Tài Khoản (Provisioning)
        </v-tab>
        <v-tab value="cleanup" class="font-weight-black text-none" prepend-icon="mdi-broom">
          Auto-Cleanup Worker 60 Ngày
        </v-tab>
      </v-tabs>

      <v-window v-model="activeTab">
        <!-- Sub-Tab 1: Tenants List & Create -->
        <v-window-item value="tenants">
          <div class="d-flex align-center justify-space-between mb-3">
            <span class="text-subtitle-2 font-weight-black text-secondary">DANH SÁCH TRƯỜNG HỌC / TRUNG TÂM B2B</span>
            <v-btn color="primary" size="small" variant="flat" class="font-weight-bold text-none" prepend-icon="mdi-plus" @click="showCreateTenantModal = true">
              Tạo Trường Mới
            </v-btn>
          </div>

          <v-table density="comfortable" hover class="border rounded-lg">
            <thead>
              <tr class="bg-grey-lighten-4">
                <th class="font-weight-black text-caption text-secondary">MÃ TRƯỜNG</th>
                <th class="font-weight-black text-caption text-secondary">TÊN TRƯỜNG HỌC</th>
                <th class="font-weight-black text-caption text-secondary text-center">SEAT LICENSE</th>
                <th class="font-weight-black text-caption text-secondary text-center">HẠN HỢP ĐỒNG</th>
                <th class="font-weight-black text-caption text-secondary text-center">TRẠNG THÁI</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="t in overview.tenants" :key="t.id">
                <td class="font-weight-bold text-caption font-weight-mono text-primary">{{ t.id }}</td>
                <td class="font-weight-black text-body-2">{{ t.name }}</td>
                <td class="text-center font-weight-bold text-caption">{{ t.license_seats }} Seats</td>
                <td class="text-center text-caption text-grey">{{ t.license_expiry }}</td>
                <td class="text-center">
                  <v-chip size="x-small" color="success" variant="flat" class="font-weight-black">ACTIVE</v-chip>
                </td>
              </tr>
              <tr v-if="!overview.tenants?.length">
                <td colspan="5" class="text-center pa-6 text-caption text-grey">
                  Chưa có Trường học nào. Bấm "Tạo Trường Mới" ở trên!
                </td>
              </tr>
            </tbody>
          </v-table>
        </v-window-item>

        <!-- Sub-Tab 2: Account Provisioning -->
        <v-window-item value="provision">
          <v-row density="comfortable">
            <v-col cols="12" md="6">
              <v-card border flat class="pa-4 bg-grey-lighten-5 rounded-lg">
                <div class="text-subtitle-2 font-weight-black text-primary mb-3">CẤP TÀI KHOẢN MỚI (PROVISION ACCOUNT)</div>
                <v-text-field
                  v-model="newProvEmail"
                  label="Email Đăng Nhập:"
                  placeholder="teacher@truongabc.edu.vn"
                  variant="outlined"
                  density="comfortable"
                  class="mb-2"
                />
                <v-text-field
                  v-model="newProvName"
                  label="Họ Và Tên:"
                  placeholder="Thầy Nguyễn Văn A"
                  variant="outlined"
                  density="comfortable"
                  class="mb-2"
                />
                <v-select
                  v-model="newProvRole"
                  :items="[{ title: 'Giảng viên / Giáo viên', value: 'teacher' }, { title: 'School Admin (Trưởng bộ môn)', value: 'admin' }]"
                  label="Cấp Độ Phân Quyền (Role):"
                  variant="outlined"
                  density="comfortable"
                  class="mb-2"
                />
                <v-text-field
                  v-model="newProvPassword"
                  label="Mật Khẩu Mặc Định:"
                  placeholder="password123"
                  variant="outlined"
                  density="comfortable"
                  class="mb-3"
                />
                <v-btn color="primary" variant="flat" block class="font-weight-black text-none" :loading="isProvisioning" @click="submitProvisioning">
                  Cấp Tài Khoản & Tạo Mã Phụ Huynh
                </v-btn>
              </v-card>
            </v-col>

            <v-col cols="12" md="6">
              <v-card border flat class="pa-4 bg-indigo-lighten-5 rounded-lg border-indigo">
                <div class="text-subtitle-2 font-weight-black text-indigo-darken-3 mb-2">QUY TẮC BẢO MẬT PHÂN QUYỀN (RBAC RULES)</div>
                <div class="text-caption text-grey-darken-3">
                  <ul class="pl-4">
                    <li class="mb-1">Tài khoản Admin tuyệt đối <strong>không mở đăng ký công khai</strong>. Chỉ do Super Admin cấp.</li>
                    <li class="mb-1">Giáo viên có thể tự đăng ký trên `/teacher` hoặc được Admin cấp tài khoản.</li>
                    <li class="mb-1">Mỗi tài khoản khởi tạo sẽ tự động được cấp 1 <strong>Mã Phụ Huynh (`PA-xxxx`)</strong> để phụ huynh tra cứu tiến độ.</li>
                  </ul>
                </div>
              </v-card>
            </v-col>
          </v-row>
        </v-window-item>

        <!-- Sub-Tab 3: Auto-Cleanup Worker -->
        <v-window-item value="cleanup">
          <v-card border flat class="pa-4 bg-teal-lighten-5 rounded-lg border-teal">
            <div class="d-flex align-center justify-space-between flex-wrap ga-2 mb-2">
              <div>
                <div class="text-subtitle-1 font-weight-black text-teal-darken-3">BẢO TRÌ LƯU TRỮ 0 ĐỒNG (SUPABASE AUTO-CLEANUP WORKER)</div>
                <div class="text-caption text-teal-darken-4">
                  Tự động dọn dẹp các file âm thanh cũ hơn 60 ngày trên Supabase Storage trong khi vẫn giữ nguyên kết quả điểm số trong CSDL.
                </div>
              </div>
              <v-btn color="teal-darken-2" variant="flat" class="font-weight-black text-none" prepend-icon="mdi-broom" @click="runAutoCleanup">
                Chạy Dọn Dẹp Ngay
              </v-btn>
            </div>
          </v-card>
        </v-window-item>
      </v-window>
    </v-card>

    <!-- Modal: Create New Tenant -->
    <v-dialog v-model="showCreateTenantModal" max-width="450">
      <v-card border rounded="lg" class="pa-4">
        <div class="text-subtitle-1 font-weight-black text-primary mb-3">Tạo Trường Học / Chi Nhánh B2B Mới</div>
        <v-text-field
          v-model="newTenantName"
          label="Tên Trường Học:"
          placeholder="Trường THCS ABC"
          variant="outlined"
          density="comfortable"
          class="mb-2"
        />
        <v-text-field
          v-model="newTenantSeats"
          label="Số Lượng Seats Mua (Học sinh):"
          type="number"
          variant="outlined"
          density="comfortable"
          class="mb-3"
        />
        <v-card-actions class="px-0 pb-0">
          <v-spacer />
          <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showCreateTenantModal = false">Hủy</v-btn>
          <v-btn color="primary" variant="flat" class="text-none font-weight-bold" @click="submitCreateTenant">Kích Hoạt Trường</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
  backendUrl: String,
  userRole: String
})

const activeUserRole = ref(props.userRole || 'super_admin')
const activeTab = ref('tenants')
const overview = ref({ total_tenants: 0, total_teachers: 0, total_students: 0, total_submissions: 0, tenants: [] })

const showCreateTenantModal = ref(false)
const newTenantName = ref('')
const newTenantSeats = ref(350)

const newProvEmail = ref('')
const newProvName = ref('')
const newProvRole = ref('teacher')
const newProvPassword = ref('password123')
const isProvisioning = ref(false)

const fetchOverview = async () => {
  try {
    const res = await fetch(`${props.backendUrl}/api/admin/overview`)
    if (res.ok) {
      overview.value = await res.json()
    }
  } catch (e) {
    console.error('Fetch admin overview error:', e)
  }
}

const submitCreateTenant = async () => {
  if (!newTenantName.value.trim()) return
  try {
    const res = await fetch(`${props.backendUrl}/api/admin/tenants/create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: newTenantName.value.trim(),
        license_seats: Number(newTenantSeats.value) || 350
      })
    })
    if (res.ok) {
      showCreateTenantModal.value = false
      newTenantName.value = ''
      await fetchOverview()
    }
  } catch (e) {
    alert('Lỗi tạo trường: ' + e.message)
  }
}

const submitProvisioning = async () => {
  if (!newProvEmail.value.trim() || !newProvName.value.trim()) return
  isProvisioning.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/admin/provision-account`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: newProvEmail.value.trim(),
        name: newProvName.value.trim(),
        role: newProvRole.value,
        password: newProvPassword.value.trim()
      })
    })
    if (res.ok) {
      alert('Đã cấp tài khoản thành công!')
      newProvEmail.value = ''
      newProvName.value = ''
      await fetchOverview()
    }
  } catch (e) {
    alert('Lỗi cấp tài khoản: ' + e.message)
  } finally {
    isProvisioning.value = false
  }
}

const runAutoCleanup = async () => {
  try {
    const res = await fetch(`${props.backendUrl}/api/admin/auto-cleanup`, { method: 'POST' })
    if (res.ok) {
      const data = await res.json()
      alert(data.message)
    }
  } catch (e) {
    alert('Lỗi auto-cleanup: ' + e.message)
  }
}

onMounted(() => {
  fetchOverview()
})
</script>

<style scoped>
.bg-gradient-dark {
  background: linear-gradient(135deg, #212121 0%, #000000 100%);
}
</style>
