package dev.miramontes.spaghetti.ui.home

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.fragment.app.Fragment
import dev.miramontes.spaghetti.R
import dev.miramontes.spaghetti.library.generateDebugSpaghettiString

class HomeFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val root = inflater.inflate(R.layout.fragment_home, container, false)
        val textView = root.findViewById<TextView>(R.id.amount)
        var spaghetti =
            generateDebugSpaghettiString()
        textView.text = spaghetti.substring(0, spaghetti.length - 3)
        return root
    }
}