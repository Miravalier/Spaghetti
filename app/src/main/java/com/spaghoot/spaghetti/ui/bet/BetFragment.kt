package com.spaghoot.spaghetti.ui.bet

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.lifecycle.Observer
import androidx.lifecycle.ViewModelProviders
import com.spaghoot.spaghetti.R

class BetFragment : Fragment() {

    private lateinit var slideshowViewModel: BetViewModel

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        slideshowViewModel =
            ViewModelProviders.of(this).get(BetViewModel::class.java)
        val root = inflater.inflate(R.layout.fragment_bet, container, false)

        return root
    }
}