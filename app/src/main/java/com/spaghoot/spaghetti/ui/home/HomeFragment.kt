package com.spaghoot.spaghetti.ui.home

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProviders
import com.spaghoot.spaghetti.R
import com.spaghoot.spaghetti.library.generateDebugSpaghettiString

class HomeFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val root = inflater.inflate(R.layout.fragment_home, container, false)
        val textView = root.findViewById<TextView>(R.id.amount)
        var spaghetti = generateDebugSpaghettiString()
        textView.text = spaghetti.substring(0, spaghetti.length - 3)
        return root
    }
}