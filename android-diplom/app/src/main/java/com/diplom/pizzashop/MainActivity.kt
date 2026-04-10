package com.diplom.pizzashop

import android.annotation.SuppressLint
import android.graphics.Color
import android.os.Build
import android.os.Bundle
import android.view.KeyEvent
import android.view.View
import android.view.ViewGroup
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.google.android.material.floatingactionbutton.FloatingActionButton

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView
    private lateinit var speedDialContainer: LinearLayout
    private var isMenuOpen = false
    private var currentRole = "guest"
    
    // Цвета
    private val colorInactiveIcon = Color.parseColor("#8899AABB")
    private val colorActiveIcon = Color.parseColor("#EA670A")
    private val colorInactiveText = Color.parseColor("#FFFFFF")
    private val colorActiveText = Color.parseColor("#EA670A")

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // 2. Убираем тулбар
        supportActionBar?.hide()

        webView = findViewById(R.id.webview)
        speedDialContainer = findViewById(R.id.speedDialContainer)

        // 4. Настройки WebView
        val settings = webView.settings
        settings.javaScriptEnabled = true
        settings.domStorageEnabled = true
        settings.useWideViewPort = true
        settings.loadWithOverviewMode = true
        settings.setSupportZoom(false)
        settings.displayZoomControls = false
        settings.textZoom = 100
        
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            settings.mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
        }

        webView.webViewClient = object : WebViewClient() {
            override fun onPageFinished(view: WebView?, url: String?) {
                super.onPageFinished(view, url)
                fetchUserRole()
                // 3. Скрываем корзину внутри WebView, так как она теперь только в доке
                hideCartInWebView()
            }
        }

        // Загрузка главной страницы
        webView.loadUrl("http://10.0.2.2:5173/")
        
        setupBottomBar()
    }

    // Скрываем нативную корзину на сайте через JS
    private fun hideCartInWebView() {
        webView.evaluateJavascript("""
            (function() {
                var cartBtn = document.querySelector('[data-testid="cart-button"]');
                if (cartBtn) cartBtn.style.display = 'none';
                var cartSection = document.getElementById('cart-section');
                if (cartSection) cartSection.style.display = 'none';
            })()
        """.trimIndent(), null)
    }

    private fun setupBottomBar() {
        val itemMenu = findViewById<LinearLayout>(R.id.itemMenu)
        val itemAI = findViewById<LinearLayout>(R.id.itemAI)
        val itemCart = findViewById<LinearLayout>(R.id.itemCart)
        val itemMore = findViewById<LinearLayout>(R.id.itemMore)

        val resetAll = {
            listOf(itemMenu, itemAI, itemCart, itemMore).forEach { setInactive(it) }
        }

        // 🍕 Меню
        itemMenu.setOnClickListener {
            resetAll(); setActive(itemMenu); closeMenu()
            webView.loadUrl("http://10.0.2.2:5173/")
        }

        // 🤖 AI
        itemAI.setOnClickListener {
            resetAll(); setActive(itemAI); closeMenu()
            webView.evaluateJavascript(
                "document.querySelector('[data-testid=\"ai-widget\"]')?.click()", null
            )
        }

        // 🛒 Корзина
        itemCart.setOnClickListener {
            resetAll(); setActive(itemCart); closeMenu()
            webView.loadUrl("http://10.0.2.2:5173/cart")
        }

        // ••• Ещё
        itemMore.setOnClickListener {
            resetAll(); setActive(itemMore)
            if (isMenuOpen) closeMenu() else openMenu()
        }
        
        setActive(itemMenu)
    }

    private fun setActive(view: LinearLayout) {
        (view.getChildAt(0) as? ImageView)?.setColorFilter(colorActiveIcon)
        (view.getChildAt(1) as? TextView)?.setTextColor(colorActiveText)
    }

    private fun setInactive(view: LinearLayout) {
        (view.getChildAt(0) as? ImageView)?.setColorFilter(colorInactiveIcon)
        (view.getChildAt(1) as? TextView)?.setTextColor(colorInactiveText)
    }

    private fun fetchUserRole() {
        webView.evaluateJavascript(
            "(function(){ return localStorage.getItem('user_role') || 'guest' })()"
        ) { roleStr ->
            val cleanRole = roleStr.replace("\"", "").trim()
            currentRole = if (cleanRole.isEmpty()) "guest" else cleanRole
            if (isMenuOpen) rebuildSpeedDial()
        }
    }

    private fun openMenu() {
        isMenuOpen = true
        speedDialContainer.removeAllViews()
        speedDialContainer.visibility = View.VISIBLE
        rebuildSpeedDial()
    }

    private fun rebuildSpeedDial() {
        speedDialContainer.removeAllViews()
        
        val items = mutableListOf<Pair<String, String>>()
        items.add("Профиль" to "http://10.0.2.2:5173/profile")
        items.add("О нас" to "http://10.0.2.2:5173/about")
        
        when (currentRole) {
            "courier" -> items.add("Мои доставки" to "http://10.0.2.2:5173/deliveries")
            "cook" -> items.add("Очередь заказов" to "http://10.0.2.2:5173/kitchen")
            "admin" -> {
                items.add("Панель управления" to "http://10.0.2.2:5173/admin")
                items.add("Статистика" to "http://10.0.2.2:5173/admin/stats")
            }
        }

        // Используем reversed() и обычный цикл для совместимости
        val reversedItems = items.asReversed()
        reversedItems.forEachIndexed { index, (label, url) ->
            val row = LinearLayout(this).apply {
                orientation = LinearLayout.HORIZONTAL
                gravity = android.view.Gravity.CENTER_VERTICAL or android.view.Gravity.END
                layoutParams = LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.WRAP_CONTENT,
                    LinearLayout.LayoutParams.WRAP_CONTENT
                ).apply { setMargins(0, 16, 0, 0) }
                alpha = 0f; translationY = 50f
                setBackgroundResource(R.drawable.bg_fab_row)
                setPadding(8, 8, 8, 8)
            }

            val text = TextView(this).apply {
                text = label
                setTextColor(Color.WHITE)
                textSize = 14f
                setPadding(16, 8, 16, 8)
            }

            val fab = FloatingActionButton(this).apply {
                setImageResource(R.drawable.ic_arrow_right)
                backgroundTintList = android.content.res.ColorStateList.valueOf(Color.parseColor("#333333"))
                layoutParams = ViewGroup.LayoutParams(100, 100)
                elevation = 8f
            }

            row.addView(text)
            row.addView(fab)
            speedDialContainer.addView(row)

            // Анимация появления
            row.animate().alpha(1f).translationY(0f)
                .setStartDelay(index * 60L).setDuration(250).start()

            row.setOnClickListener {
                closeMenu()
                webView.loadUrl(url)
            }
        }
    }

    private fun closeMenu() {
        if (!isMenuOpen) return
        isMenuOpen = false
        
        val count = speedDialContainer.childCount
        // Цикл в обратном порядке
        for (i in count - 1 downTo 0) {
            val view = speedDialContainer.getChildAt(i)
            view.animate().alpha(0f).translationY(50f)
                .setDuration(150)
                .withEndAction {
                    if (i == 0) speedDialContainer.visibility = View.GONE
                }.start()
        }
    }

    override fun onKeyDown(keyCode: Int, event: KeyEvent): Boolean {
        if (keyCode == KeyEvent.KEYCODE_BACK) {
            if (isMenuOpen) { closeMenu(); return true }
            if (webView.canGoBack()) { webView.goBack(); return true }
            finish()
            return true
        }
        return super.onKeyDown(keyCode, event)
    }

    override fun onDestroy() {
        super.onDestroy()
        webView.destroy()
    }
}
