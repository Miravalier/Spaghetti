package dev.miramontes.spaghetti

import android.annotation.SuppressLint
import android.content.Context
import android.os.Bundle
import android.webkit.JavascriptInterface
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Toast
import androidx.activity.ComponentActivity


class WebAppInterface(private val mContext: Context) {
    @JavascriptInterface
    fun showToast(toast: String) {
        Toast.makeText(mContext, toast, Toast.LENGTH_SHORT).show()
    }
}


class MainActivity : ComponentActivity() {
    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val webView = WebView(applicationContext)
        webView.settings.javaScriptEnabled = true
        webView.settings.domStorageEnabled = true
        setContentView(webView)
        webView.clearCache(true)
        webView.loadUrl("https://spaghetti.miramontes.dev")
        webView.addJavascriptInterface(WebAppInterface(this), "Android")
        webView.webViewClient = WebViewClient()
    }
}